#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 谢泽华
# @Date: 2026/6/17 16:11
# @Desc: 打码平台识别验证码
import asyncio
import base64
from urllib.parse import urljoin
import aiohttp
import requests
import json

token = json.load(open("token.json", "r", encoding="utf-8"))["token"]

async def fetch(url,session, sem:asyncio.Semaphore,page,captcha_answer,headers):
    params = {'page': page}
    if page == 1:
        params['force_captcha'] = '1'
    else:
        params['captcha_answer'] = captcha_answer
    async with sem:
        try:
            async with session.get(url,params=params, headers=headers) as response:
                data = await response.json()
                image_url = urljoin(url, data['data']['captcha']['image_url'])
                if not data.get("success"):
                    return image_url, None  # 验证码错误
                items = data.get('data',{}).get("items",[])
            return image_url,items  # 成功，可能为空列表
        except Exception as e:
            print(f"请求失败 {url}: {e}")
            return None, None

async def download_and_ocr(full_url, sem:asyncio.Semaphore,session, headers):
    if not full_url:
        return None
    async with sem:
        try:
            async with session.get(full_url, headers=headers) as img_resp:
                img_data = await img_resp.read()
                # with open("test.png", "wb") as f:
                #     f.write(img_data)
                b = base64.b64encode(img_data).decode()
                return b
        except Exception as e:
            print(f"验证码下载失败: {e}")
            return None

async def verify(base64_img):
    if not base64_img:
        return None
    url = "https://www.jfbym.com/api/YmServer/testCustomApi"
    data = {
        ## 关于参数,一般来说有3个;不同类型id可能有不同的参数个数和参数名,找客服获取
        "image": base64_img,
        "type": "50100",
        "token":token,
    }
    _headers = {
        "Content-Type": "application/json"
    }
    response = requests.request("POST", url, headers=_headers, json=data).json()
    return response["data"]["data"]


async def main():
    filtered_list = []
    page = 1  # 当前要抓取的页码，从第 1 页开始
    text = ''  # 用于存储上一次识别出的验证码答案（字符串），初次为空
    base_url = 'https://tc.xfei.tech/playground/trademark-opposition/ZW823fJKaj8Sf8NrQCI/zh/api/records'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36',
    }

    sem = asyncio.Semaphore(10)
    async with aiohttp.ClientSession() as session:
        while page <= 90:
            print(f"正在抓取第 {page} 页")
            image_url,items = await fetch(base_url, session, sem,page,text,headers)
            # 处理请求异常
            if image_url is None:
                print("请求失败，等待后重试")
                await asyncio.sleep(1)
                continue
            # 处理验证码错误（items 为 None）
            if items is None:
                print("验证码错误，重新识别")
                base_img = await download_and_ocr(image_url, sem, session, headers)
                if not base_img:
                    print("验证码下载失败，重试")
                    await asyncio.sleep(1)
                    continue
                captcha_text = await verify(base_img)
                print(captcha_text)

                if not captcha_text:
                    print("验证码识别失败，重试")
                    await asyncio.sleep(1)
                    continue
                text = captcha_text
                continue  # 重试当前页

            # 成功获取数据（items 可能为空列表）
            # 过滤符合条件的条目
            filtereds = [
                item for item in items
                if item.get("risk_level") == 'high' and "审查中" in item.get("legal_status", "")
            ]
            filtered_list.extend(filtereds)
            print(f"当前页收集 {len(filtereds)} 条，累计 {len(filtered_list)} 条")

            # 预取下一页验证码（当前页返回的 image_url 是新的验证码图片）
            base_img = await download_and_ocr(image_url, sem, session, headers)
            if base_img:
                captcha_text = await verify(base_img)
                print("预取下一页验证码",captcha_text)
                if captcha_text:
                    text = captcha_text  # 仅当识别成功才更新
                else:
                    print("下一页验证码识别失败，将使用旧答案（可能导致重试）")
            else:
                print("下一页验证码下载失败，将使用旧答案")

            page += 1

    print(f"总计符合条件条目数: {len(filtered_list)}")


if __name__ == '__main__':
    asyncio.run(main())

