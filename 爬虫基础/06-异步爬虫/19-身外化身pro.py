#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 谢泽华
# @Date: 2026/6/13 22:00
# @Desc:

import re
from 爬虫基础.lib import headers
import asyncio
import aiohttp
from urllib.parse import urljoin
from parsel import Selector
from motor.motor_asyncio import AsyncIOMotorClient,AsyncIOMotorCollection


async def asve_chapter_mongo(
    collection:AsyncIOMotorCollection,
    chapter:dict
):
    """异步入库：基于 URL 去重更新（upsert）"""
    await collection.update_one(
        {'url': chapter['url']},
        {'$set':chapter},
        upsert=True
    )
    print(f"已入库：{chapter['title']}")


async def count_non_blank(text_list:list)->int:
    """统计段落列表中所有非空白字符（不包括空格、换行、制表符等）"""
    total = 0
    for para in text_list:
        # 去除空白字符（空格、\n、\t等）后计算长度
        total += len(re.sub(r'\s+', '', para))
    return total

async def fetch(
        session:aiohttp.ClientSession,
        sem:asyncio.Semaphore,
        url:str)->tuple:
    """带信号量和超时的请求"""
    async with sem:
        try:
            import random
            await asyncio.sleep(random.uniform(0.1,0.5))
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                status = resp.status
                html = await resp.text()
                return status, html, url
        except Exception as e:
            print(f"请求失败 {url}: {e}")
            return None, None,url


# 获取内容url、下一页url
async def get_article_urls(base_url:str, html:str)->tuple:
    content_url_list = []
    selector = Selector(text=html)
    articles = selector.xpath('//div[@class="chapter-grid"]/article')
    next_url = selector.xpath('//nav[@class="novel-pagination"]/a[contains(text(),"下一页")]/@href').get()
    if next_url:
        next_url = urljoin(base_url, next_url)
    else:
        next_url = None

    for article in articles:
        content = article.xpath('.//a/@href').get()
        content_url = urljoin(base_url, content)
        content_url_list.append(content_url)

    return content_url_list, next_url

# 解析章节内容
async def content_text(html:str,url:str)->dict:
    selector = Selector(text=html)
    title = selector.xpath('//h1/text()').get()
    paragraphs = selector.xpath('//div[@class="chapter-body"]/p/text()').getall()
    content_str = '\n'.join(paragraphs)

    non_blank_count = await count_non_blank(paragraphs)
    title_number = re.findall(r'\d+',title)
    return {
        "url":url,
        "title_number": title_number[0],
        "title":title,
        "non_blank_count":non_blank_count,
        "paragraphs":content_str
    }

async def main():
    import time
    start = time.time()
    base_url = "https://async.tc.xfei.tech/playground/async-novel/ZW82bkWjajCR_8bwS9k/zh/"
    # 1. 异步 MongoDB 客户端
    motor_client = AsyncIOMotorClient("mongodb://crawler:crawler123@192.168.1.25:27017")
    db = motor_client.spiders
    collection = db["novel-chapters"]

    content_urls_list = []
    semaphore = asyncio.Semaphore(20)
    async with aiohttp.ClientSession() as session:
        # 2. 顺序翻页收集所有文章 URL
        current_url = base_url
        while True:
            status, html, fetched_url = await fetch(session, semaphore, current_url)
            if status != 200:
                print(f"获取列表页失败: {current_url}, 状态码 {status}")
                break

            content_url_list, next_url = await get_article_urls(base_url,html)
            content_urls_list.extend(content_url_list)
            print(f"已收集 {len(content_urls_list)} 个文章链接，当前页: {current_url}")
            if next_url:
                base_url = urljoin(base_url, next_url)
            else:
                break
            current_url = next_url
        # 3. 并发请求所有文章详情
        tasks = [fetch(session, semaphore, url) for url in content_urls_list]
        # 4. 逐一解析并异步入库
        success_count = 0
        failed_count = 0
        for status, html, url in await asyncio.gather(*tasks):
            if status != 200:
                print(f"获取文章失败: {url}, 状态码 {status}")
                continue
            try:
                # 数据解析
                chapter_data = await content_text(html, url)
                # 异步入库
                await asve_chapter_mongo(collection, chapter_data)
                success_count += 1
            except Exception as e:
                failed_count += 1
                print(f"数据解析或入库失败: {e}")
            done_count = success_count + failed_count
            print(f"进度：{done_count}/{len(content_urls_list)}，成功：{success_count}，失败：{failed_count}")

    motor_client.close()
    print(f"全部完成，共处理 {len(content_urls_list)} 章")
    print(f"总耗时：{time.time()-start:2f} 秒")

if __name__ == "__main__":
    asyncio.run(main())