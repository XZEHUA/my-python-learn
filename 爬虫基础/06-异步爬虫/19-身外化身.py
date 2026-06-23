#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 谢泽华
# @Date: 2026/6/11 16:08
# @Desc:

import re
from 爬虫基础.lib import headers
import asyncio
import aiohttp
from urllib.parse import urljoin
from parsel import Selector

base_url = "https://async.tc.xfei.tech/playground/async-novel/ZW82bkWjai3u_5rv1V8/zh?page=1&size=100"          # 网站首页或列表页第一页


def extract_chapter_number(chapter_text):
    """从章节标题中提取数字编号，例如 '第123章 标题' -> 123"""
    match = re.search(r'(\d+)', chapter_text)
    return int(match.group(1)) if match else 0

def count_non_blank(text_list):
    """统计段落列表中所有非空白字符（不包括空格、换行、制表符等）"""
    total = 0
    for para in text_list:
        # 去除空白字符（空格、\n、\t等）后计算长度
        total += len(re.sub(r'\s+', '', para))
    return total

async def fetch(session, sem, url):
    """带信号量和超时的请求"""
    async with sem:
        try:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                status = resp.status
                html = await resp.text()
                return status, html
        except Exception as e:
            print(f"请求失败 {url}: {e}")
            return None, None

async def get_article_urls(html, base_url):
    """从列表页提取文章链接"""
    selector = Selector(text=html)
    articles = selector.xpath('//article')
    urls = []
    for article in articles:
        # 提取当前 article 下的所有 a 标签 href（相对路径）
        hrefs = article.xpath('.//a/@href').getall()
        for href in hrefs:
            full_url = urljoin(base_url, href)
            urls.append(full_url)
    # 去重（可选）
    return list(set(urls))

async def get_next_page_url(html, base_url):
    """从列表页提取下一页链接"""
    selector = Selector(text=html)
    next_page = selector.xpath("//nav/a[text()='下一页']/@href").get()
    if next_page:
        return urljoin(base_url, next_page)
    return None

async def crawl_articles(session, sem, article_urls):
    """并发爬取一组文章链接"""
    tasks = [fetch(session, sem, url) for url in article_urls]
    results = await asyncio.gather(*tasks)
    articles_data = []
    for (status, html), url in zip(results, article_urls):
        if status == 200:
            # 这里可以进一步解析文章内容，或保存 html
            selector = Selector(text=html)
            # 正文段落
            paragraphs = selector.xpath('//div[@class="chapter-body"]/p/text()').getall()
            non_blank_count = count_non_blank(paragraphs)
            # 章节标题
            chapter_title = selector.xpath('//h1/text()').get()
            chapter_num = extract_chapter_number(chapter_title) if chapter_title else 0
            print(f"成功: {url}, 章节 {chapter_title} , 非空白字符数 {non_blank_count}")
            print(
                {"chapter_num": chapter_num,
                 "non_blank_chars": non_blank_count,
                 "paragraphs": paragraphs,
                 "url": url}
            )
            articles_data.append({
                "chapter_num": chapter_num,
                "non_blank_chars": non_blank_count,
                "url": url
            })
        else:
            print(f"失败: {url}")
    return articles_data

async def main():
    all_articles = []
    sem = asyncio.Semaphore(20)          # 全局并发限制
    async with aiohttp.ClientSession() as session:
        current_url = base_url
        page_num = 1

        while current_url:
            print(f"\n正在爬取第 {page_num} 页: {current_url}")
            status, html = await fetch(session, sem, current_url)
            if status != 200:
                print(f"第 {page_num} 页请求失败，停止翻页")
                break

            # 1. 提取当前页的文章链接
            article_urls = await get_article_urls(html, base_url)
            print(f"第 {page_num} 页找到 {len(article_urls)} 篇文章")

            # 2. 并发爬取这些文章
            data = await crawl_articles(session, sem, article_urls)
            all_articles.extend(data)
            # 3. 获取下一页链接
            next_url = await get_next_page_url(html, base_url)
            if next_url and next_url != current_url:
                current_url = next_url
                page_num += 1
            else:
                break

    if all_articles:
        # 找出非空白字符数最多的章节
        max_article = max(all_articles, key=lambda x: x["non_blank_chars"])
        # 按格式输出：章节编号-字符数
        print(f"\n答案：{max_article['chapter_num']}-{max_article['non_blank_chars']}")
    else:
        print("未抓到任何文章")

if __name__ == "__main__":
    asyncio.run(main())