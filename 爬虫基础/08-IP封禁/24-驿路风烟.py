#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 谢泽华
# @Date: 2026/7/1 11:58
# @Desc: IP 代理

import asyncio
import json
import aiohttp
import requests

with open('key.json', 'r', encoding='utf-8') as f:
    cfg = json.load(f)
AUTH_KEY = cfg.get("AUTH_KEY")
GET_IP_API = "https://share.proxy.qg.net/get"
GET_IP_API_PARAMS = {"key": AUTH_KEY, "num": 1, "isp": 0, "distinct": "true"}
TARGET_URL = "https://logi.tc.xfei.tech/playground/logistics-query/ZW82CaOeakhM_39fTKc/zh/api/track"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def get_one_proxy():
    """同步获取一个代理（因提取频率低，放在执行器里跑，不阻塞事件循环）"""
    resp = requests.get(GET_IP_API, params=GET_IP_API_PARAMS, timeout=5)
    data = resp.json()
    if data.get('code') == 'SUCCESS':
        return data['data'][0]['server']
    return None

async def fetch_with_proxy(session, tn, proxy_server):
    """使用指定代理查询运单"""
    proxy_url = f"http://{proxy_server}"
    payload = {"tracking_number": tn}
    try:
        async with session.post(
            TARGET_URL,
            json=payload,
            proxy=proxy_url,          # 注意：这里是 proxy（单数）
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
    # 要查询的运单号列表
    tracking_numbers = [f"OE2026061088{mun}" for mun in range(60, 80)]
    total_orders = len(tracking_numbers)
    total_distance = 0
    matched_orders = []
    request_count = 0   # 当前 IP 已请求次数
    current_proxy = None

    # 创建一个 Session 复用连接（但代理会变）
    async with aiohttp.ClientSession() as session:
        for idx, tn in enumerate(tracking_numbers, 1):
            # 1. 每请求 4 次，或者代理为空，就换一个新 IP
            if request_count >= 4 or current_proxy is None:
                # 在线程池中执行同步的 requests 请求，避免阻塞
                loop = asyncio.get_running_loop()
                current_proxy = await loop.run_in_executor(None, get_one_proxy)
                if not current_proxy:
                    print("❌ 获取代理失败，等待 2 秒重试...")
                    await asyncio.sleep(2)
                    current_proxy = await loop.run_in_executor(None, get_one_proxy)
                print(f"🔄 切换新代理: {current_proxy}")
                request_count = 0   # 重置计数器

            print(f"[{idx}/{total_orders}] 查询 {tn}，使用代理 {current_proxy}")
            result = await fetch_with_proxy(session, tn, current_proxy)
            request_count += 1

            # 2. 处理结果
            if "error" in result:
                print(f"  ❌ 请求失败: {result['error']}")
                # 遇到错误立即强制换 IP（将计数器设为 4，下一次循环会换）
                request_count = 4
                continue

            if result.get('success'):
                data = result['data']
                status = data.get('status')
                service = data.get('service')
                distance_str = data.get('distance', '0 km')
                print(f"  📍 status={status}, service={service}, distance={distance_str}")

                if status == "运输中" and service == "标准快递":
                    import re
                    dist_km = int(re.sub(r'[^\d]', '', distance_str))
                    total_distance += dist_km
                    matched_orders.append((tn, dist_km))
                    print(f"  ✅ 匹配！累计距离: {total_distance} km")
            else:
                print(f"  ❌ 业务返回失败: {result}")

            # 3. 每次请求间隔 0.3 秒
            await asyncio.sleep(0.3)

    # 输出结果
    print("\n" + "="*50)
    print(f"符合条件的运单数: {len(matched_orders)}")
    for tn, d in matched_orders:
        print(f"  • {tn} : {d} km")
    print(f"🎯 最终提交总和: {total_distance}")
    print("="*50)

if __name__ == "__main__":
    asyncio.run(main())