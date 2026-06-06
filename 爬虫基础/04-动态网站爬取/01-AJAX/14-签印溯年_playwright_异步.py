#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 谢泽华
# @Date: 2026/5/21 12:22
# @Desc:

import asyncio
import re
import pymongo
from playwright.async_api import async_playwright
from pymongo.errors import DuplicateKeyError

client = pymongo.MongoClient("mongodb://crawler:crawler123@192.168.1.25:27017")
db = client.spiders # client["spiders"]
collection = db.movies_14 # db["movies_14"]


collection.create_index("电影", unique=True)

async def safe_get_text(locator):
    """安全获取文本，元素不存在返回空字符串，永不报错"""
    if await locator.count() > 0:
        return( await locator.inner_text()).strip()
    return ""


async def get_content():

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        url = "https://tc.xfei.tech/playground/movie-list-ajax-token/ZW82KVoNaheFfyBxAOo/zh"
        await page.goto(url,wait_until="networkidle")
        rating_counts = 0
        page_num = 1
        while True:
            print(f"\n===== 正在爬取第 {page_num} 页 =====")
            await page.wait_for_selector(".movie-item", timeout=10000)

            movie_lists = page.locator(".movie-item")
            count =await movie_lists.count()
            print("总电影数：",count)

            for i in range(count):
                item = movie_lists.nth(i)
                title = await item.locator("div.movie-title").inner_text()

                movie_details = await  safe_get_text(item.locator("div.movie-details"))

                year_match = re.search(r"\d{4}", movie_details)
                year = year_match.group() if year_match else "未知"

                country_match = re.search(r'\|\s*(.+?)\s*\|', movie_details)
                country = country_match.group(1) if country_match else "未知"

                director_match = re.search(r"\|\s*([^|]+)\s*$", movie_details)
                director = director_match.group(1).strip() if director_match else "未知"

                enres = await item.locator("div.movie-genres").inner_text()

                summary = await safe_get_text(item.locator("div.movie-summary"))

                rating_count_math = await item.locator("div.movie-rating-count").inner_text()
                rating_count =  re.search(r"\d+", rating_count_math).group()
                rating_counts += int(rating_count)
                data = {
                    "电影":title,
                    "上映年份":year,
                    "国家":country,
                    "导演":director,
                    "类型":enres,
                    "简介":summary,
                    "评分人数":rating_count,
                }
                try:
                    success = 0
                    collection.insert_one(data)
                    print(f"✅ 插入成功：{title}")
                    success += 1
                except DuplicateKeyError as e:
                    print(f"⚠️ 已存在，跳过：{title}")
                    continue
            print(f"第 {page_num} 页 成功插入 {success} 条数据")

            next_btn = page.locator(".pagination-btn", has_text="下一页")

            if await next_btn.count() > 0 and await next_btn.is_visible():
                btn_class = await next_btn.get_attribute("class")
                if btn_class and "disabled" in btn_class:
                    print("✅ 已经是最后一页，爬取结束！")
                    break
                print("点击下一页...")
                await next_btn.scroll_into_view_if_needed()
                await next_btn.click()
                await page.wait_for_load_state("networkidle")
                await page.wait_for_selector(".movie-item", timeout=10000)
                page_num += 1
            else:
                print("✅ 已经到最后一页，爬取结束！")
                break

        data_list = collection.find()  # 返回游标
        item = list(data_list)
        print(f"总数为：{len(item)}")
        await browser.close()


asyncio.run(get_content())


