#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 谢泽华
# @Date: 2026/6/8 14:46
# @Desc: 异步

import asyncio
import aiohttp
import time
from 爬虫基础.lib import headers

url = "https://tc.xfei.tech/test/timeout"

async def fetch(session, semaphore, i):
    async with semaphore:          # 控制并发数量
        async with session.get(url, headers=headers) as response:
            status = response.status
            data = await response.json()
            print(i+1, status, data)
            return data

async def main():
    start = time.time()
    semaphore = asyncio.Semaphore(20)   # 最多同时 10 个请求

    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(100):
            tasks.append(fetch(session, semaphore, i))
        results = await asyncio.gather(*tasks)   # 并发执行所有任务

    elapsed = time.time() - start
    print(f"总耗时: {elapsed:.2f} 秒")

if __name__ == "__main__":
    asyncio.run(main())