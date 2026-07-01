#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 谢泽华
# @Date: 2026/6/30 17:16
# @Desc: 滑块验证码

import asyncio
import re
from urllib.parse import urljoin
import aiohttp
import json
import base64
import requests
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorClient

MONGO_URI = "mongodb://crawler:crawler123@192.168.1.25:27017"
MONGO_DB = "spiders"
MONGO_COL = "ticket_inquiry_23"
token = json.load(open(r"token.json", "r", encoding='utf-8'))["token"]

async def fetch(session,sem,url,params,headers):
    '''
    异步发送 HTTP GET 请求，并根据请求内容和响应状态码返回不同类型的数据。

    该函数用于处理三种场景：
    1. 请求的是验证码背景图片（URL 中包含 'background'），则读取响应二进制数据并返回 Base64 编码的字符串。
    2. 正常响应（状态码 200），则解析 JSON 并提取 `data['data']['items']` 列表返回。
    3. 触发验证码限制（状态码 403），则解析 JSON 中的验证码背景图 URL（`data.data.captcha.background_url`）并返回该 URL 字符串。
    其他状态码或异常情况未做显式处理，可能返回 None 或抛出异常。

    Args:
        session (aiohttp.ClientSession): 已创建的 aiohttp 客户端会话对象，用于发起请求。
        sem (asyncio.Semaphore): 信号量，用于控制并发请求数量，防止资源耗尽。
        url (str): 请求的完整 URL 地址。
        params (dict): URL 查询参数字典，键值对将被拼接到 URL 后。
        headers (dict): 请求头字典，如 User-Agent、Cookie 等。

    Returns:
        Union[list, str, None]:
            - 若请求图片（background），返回 Base64 编码的图片字符串。
            - 若状态码 200，返回包含数据项的列表（`list`）。
            - 若状态码 403，返回验证码背景图的相对路径或完整路径字符串（需由调用方拼接 base URL）。
            - 若遇到其他状态码或解析失败，可能返回 `None`（当前未显式返回，视具体实现而定）。

    Raises:
        aiohttp.ClientError: 当网络请求失败时可能抛出。
        KeyError: 若响应 JSON 结构不符合预期（如缺少 `data` 或 `items` 等字段）。

    Note:
        - 该函数是异步的，需在 async 函数中使用 `await` 调用。
        - 对于状态码 403，假设返回的 JSON 一定包含 `data.data.captcha.background_url` 字段。
        - 对于图片请求，通过 URL 中是否包含子字符串 `'background'` 来识别，而非通过 Content-Type，需确保调用时 URL 命名符合此规则。
    '''
    async with sem:
        async with session.get(url,params=params,headers=headers) as resp:
            # 请求验证码背景图片（URL 含 'background'）
            if "background" in url:
                data = await resp.read()
                return base64.b64encode(data).decode()
            # 正常获取数据列表（状态码 200）
            if resp.status == 200:
                data = await resp.json()
                items = data["data"]['items']
                return items
            # 触发验证码校验（状态码 403），返回验证码背景图 URL
            if resp.status == 403:
                data = await resp.json()
                background_url = data.get('data',{}).get('captcha',{}).get('background_url')
                return background_url

# 识别验证码
async def verify(base64_img):
    if not base64_img:
        return None
    url = "https://www.jfbym.com/api/YmServer/testCustomApi"
    data = {
        ## 关于参数,一般来说有3个;不同类型id可能有不同的参数个数和参数名,找客服获取
        "image": base64_img,
        "type": "22222",
        "token":token,
        "extra":True
    }
    _headers = {
        "Content-Type": "application/json"
    }
    response = requests.request("POST", url, headers=_headers, json=data).json()
    return response

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
    await create_indexes('train_no', motor_client)
    delta_x = None
    page = 1
    price = 0
    url = "https://tc.xfei.tech/playground/ticket-query/ZW829wqNakb7f-U9_oU/zh/api/records"

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36',
    }
    # 并发信号量
    sem = asyncio.Semaphore(10)
    # 异步创建 aiohttp 客户端会话并将其命名为 session
    async with aiohttp.ClientSession() as session:
        while page < 13:
            print(f"正在抓取第{page}页")
            # 构建载荷
            params = {
                "page": page
            }
            if page > 1 and delta_x is not None:
                params['captcha_delta_x'] = delta_x
            # 网络请求
            items = await fetch(session,sem,url,params,headers)
            # 判断网络请求是否为列表，车票数据为 list 类型
            if isinstance(items, list):
                for item in items:
                    # 数据入库
                    await save_chapter_mongo(collection, item, 'train_no')
                    # 提取价格，转换为 int 类型
                    lowest_price = item.get("lowest_price")
                    price_find = re.findall(r"[\d,]+",lowest_price)[0]
                    price += int(price_find.replace(',', ''))
                page += 1
                # print(params)
            else:
                # 拼接验证码路径
                image_url = urljoin(url,items)
                # print(image_url)
                # 访问验证码，返回base64格式
                img_base_64 = await fetch(session,sem,image_url,params,headers)
                # 平台打码
                img_res = await verify(img_base_64)
                # print(img_res)
                # 验证码参数赋值
                delta_x = img_res.get("data",{}).get("data")

    print(price)
if __name__ == "__main__":
    asyncio.run(main())