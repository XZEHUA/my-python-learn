#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 谢泽华
# @Date: 2026/7/1 18:17
# @Desc: IP 封禁 突破，自己写的

import asyncio
import json
import re

import aiohttp
import requests
from motor.motor_asyncio import AsyncIOMotorClient
from 爬虫基础.lib import  create_indexes,save_chapter_mongo

# ====================== 配置 ===================
with open('key.json', 'r', encoding='utf-8') as f:
    cfg = json.load(f)
AUTH_KEY = cfg.get("AUTH_KEY")
GET_IP_API = "https://share.proxy.qg.net/get"
GET_IP_API_PARAMS = {"key": AUTH_KEY, "num": 1, "isp": 0, "distinct": "true"}
TARGET_URL = "https://logi.tc.xfei.tech/playground/logistics-query/ZW82CaOeakhM_39fTKc/zh/api/track"
HEADERS = {"User-Agent": "Mozilla/5.0"}
MONGO_URI = "mongodb://crawler:crawler123@192.168.1.25:27017"
MONGO_DB = "spiders"
MONGO_COL = "express_delivery_24"

# ====================== 函数 ====================
async def get_proxies():
    '''
    代理IP获取
    '''
    resp = requests.get(url=GET_IP_API,params=GET_IP_API_PARAMS, headers=HEADERS)
    data = resp.json()
    if data.get('code') == 'SUCCESS':
        return data['data'][0]['server']

async def fetch_with_proxy(session, tn, proxy_server):
    '''
    使用代理IP，发送网络请求
    '''
    proxy_url = f"http://{proxy_server}"
    payload = {"tracking_number": tn}
    try:
        async with session.post(
            TARGET_URL,
            json=payload,       # 载荷
            proxy=proxy_url,    # 代理IP
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=10)
        ) as resp:
            if resp.status == 200:
                return await resp.json()
            else:
                return {"error": f"状态码 {resp.status}"}
    except Exception as e:
        return {"error": str(e)}

async def main():
    request_count = 0
    current_proxy = None
    distance_count = 0

    motor_client = AsyncIOMotorClient(MONGO_URI)
    collection = motor_client[MONGO_DB][MONGO_COL]
    await create_indexes('tracking_number',collection)

    tracking_numbers = [f"OE2026061088{mun}" for mun in range(60, 80)]
    async with aiohttp.ClientSession() as session:
        for tn in tracking_numbers:
            if request_count >=6 or current_proxy is None:
                request_count = 0
                current_proxy = await get_proxies()
                print(f"代理IP：{current_proxy}")

            retry_times = 3
            for attempt in range(retry_times):
                try:
                    resp = await fetch_with_proxy(session, tn, current_proxy)
                    request_count += 1
                    resp_data = resp.get("data",{})
                    await save_chapter_mongo(collection,resp_data,'tracking_number')
                    status = resp_data.get('status')
                    service = resp_data.get('service')
                    distance_str = resp_data.get("distance",'')
                    if status == '运输中' and service == "标准快递":
                        dist_km = int(re.sub(r'[^\d]', '', distance_str))
                        distance_count += dist_km
                    break
                except Exception as e:
                    print(f"运单 {tn} 请求失败：{e}，第 {attempt + 1} 次重试，换IP")
                    # 换一个新IP，重置计数器
                    current_proxy = await get_proxies()
                    request_count = 0
                    await asyncio.sleep(0.5)  # 稍等再重试
                    if attempt == retry_times - 1:
                        print(f"运单 {tn} 重试 {retry_times} 次仍失败，跳过")
    print(f"总里程为{distance_count}")

if __name__ == '__main__':
    asyncio.run(main())