#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 谢泽华
# @Date: 2026/6/29 22:42
# @Desc: 点选验证码

import asyncio
import json
from urllib.parse import urljoin
import aiohttp
import base64

import requests
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorClient

MONGO_URI = "mongodb://crawler:crawler123@192.168.1.25:27017"
MONGO_DB = "spiders"
MONGO_COL = "Job_hunting_22"
token = json.load(open(r"token.json", "r", encoding='utf-8'))["token"]
print(token)

# 图片转base_64编码
async def img_base_64(f):
    return  base64.b64encode(f).decode()

# 打码平台
async def verify(token, b, targets):
    '''
    返回
    {
    'msg': '识别成功',
    'code': 10000,
    'data': {
    'code': 0,
    'data': '317,99|308,426|501,93|116,96',
    'time': 0.06382131576538086,
    'again_number': 0,
    'again_tag': 1,
    'unique_code':
    '5c56278681e0e794e7d40026c75c255b'
        }
    }
    '''
    url = "http://api.jfbym.com/api/YmServer/customApi"
    data = {"token": token, "extra": targets, "type": 88888, "image": b}
    _headers = {
        "Content-Type": "application/json"
    }
    try:
        response = requests.request("POST", url, headers=_headers, json=data).json()
        return response
    except Exception as e:
        return e

# 异步网络请求
async def fetch_data(url, session, sem, params, headers):
    async with sem:
        # 判断是否为图片url
        if not "image" in url:
            # 数据接口
            try:
                async with session.get(url,params=params,headers=headers) as resp:
                    data = await resp.json()
                    return data
            except Exception as e:
                print(f"请求失败 {url}: {e}")
        else:
            # 获取验证码图片
            try:
                async with session.get(url,params=params,headers=headers) as resp:
                    data = await resp.read()
                    # with open("captcha.jpg","wb") as f:
                    #     f.write(data)
                    return data
            except Exception as e:
                print(f"请求失败 {url}: {e}")

# 发送验证码坐标
async def post_clicks(session, sem, targets_data, headers):
    url = "https://tc.xfei.tech/playground/job-radar/ZW82HHxMakWp_6v_4Bo/zh/api/captcha/verify"
    async with sem:
        data = await session.post(url,json=targets_data,headers=headers)
        return data


# 创建数据库索引
async def create_indexes(index,motor_client):
    collection = motor_client[MONGO_DB][MONGO_COL]
    await collection.create_index(index, unique=True)

# 数据存储
async def save_chapter_mongo(
    collection: AsyncIOMotorCollection,
    chapter: dict,
    index:str
):
    """异步入库：基于 index 去重更新（upsert）"""
    await collection.update_one(
        {index: chapter[index]},
        {'$set': chapter},
        upsert=True
    )
    print(f"已入库：{chapter[index]}")


async def main():
    motor_client = AsyncIOMotorClient(MONGO_URI)
    collection = motor_client[MONGO_DB][MONGO_COL]
    await create_indexes('id',motor_client)
    page = 1
    base_url = "https://tc.xfei.tech/playground/job-radar/ZW82HHxMakWp_6v_4Bo/zh/api/jobs"
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36',
    }
    sem = asyncio.Semaphore(10)
    async with aiohttp.ClientSession() as session:
        while page < 9:
            params = {
                "page": page
            }
            print(f"正在抓取第{page}页")
            data = await fetch_data(base_url, session, sem, params, headers)
            if data.get("success"):
                jobs_list = data.get("data", {}).get("jobs", [])
                print(jobs_list)
                for item in jobs_list:
                    await save_chapter_mongo(collection,item,"id")
                page += 1

            if data.get("data",{}).get('captcha',{}).get("image_url"):
                image_url = data.get("data",{}).get('captcha',{}).get("image_url")
                targets_list = data.get("data",{}).get('captcha',{}).get("targets",[])
                targets_str = ','.join(targets_list)
                img_url = urljoin(base_url, image_url)
                # print(f"验证码地址{img_url}")
                # print(f"点选{targets_str}")
                img = await fetch_data(img_url, session, sem, params, headers)
                img_64 = await img_base_64(img)
                resp_targets = await verify(token, img_64, targets_str)
                # print(f"打码平台返回：",resp_targets)
                # 取出坐标字符串
                coord_str = resp_targets["data"]["data"]
                # 按 | 分割多组坐标
                coord_list = coord_str.split("|")

                clicks = []
                for item in coord_list:
                    # 拆分x、y，转数字
                    x_str, y_str = item.split(",")
                    raw_x = int(x_str)
                    raw_y = int(y_str)

                    clicks.append({
                        "x": raw_x,
                        "y": raw_y
                    })

                # 组装最终提交参数
                targets_data = {
                    "page": page,
                    "clicks": clicks
                }
                # print(f"发送坐标的参数",targets_data)
                resp = await post_clicks(session, sem, targets_data, headers)
                resp_data = await resp.json()
                # print(f"发送坐标返回",resp_data)

if __name__ == '__main__':
    asyncio.run(main())