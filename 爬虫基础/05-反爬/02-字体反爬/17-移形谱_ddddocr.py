#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 谢泽华
# @Date: 2026/5/27 13:14
# @Desc: 静态字体反爬

"""
ddddocr创建映射表
"""

import asyncio
import os
import requests
from parsel import Selector
from 爬虫基础.lib import to_float,decrypt_text
from font_ddddocr import process_font_with_ddddocr



base_url = "https://tc.xfei.tech/playground/static-font-map/ZW82XxIIaiio_wDs7NY/zh/"

HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"
}

# 缓存目录
FONT_DIR = "./font"
os.makedirs(FONT_DIR, exist_ok=True)


def get_html(url):
    for i in range(4):
        url = base_url
        params = {
            "offset" : 18 * i
        }
        response = requests.get(url, params=params,headers=HEADERS)
        html = response.text
        print(f"第{i+1}页")
        print(response.url)
        yield html


# 下载字体
def download_font(*font_url):
    if not font_url:
        font_url = "https://tc.xfei.tech/static/static-font-map/fonts/jiyun-cipher.woff2"
        HEADERS = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"
        }

        filename = font_url.split("/")[-1]
        file_path = os.path.join(FONT_DIR, filename)
        response = requests.get(font_url, headers = HEADERS)
        if os.path.exists("./font/jiyun-cipher.woff2"):
            print("字体文件已存在，跳过下载。")
            return file_path, filename

        print("正在下载字体文件...")
        with open('./font/jiyun-cipher.woff2', 'wb') as f:
            f.write(response.content)
        print("字体下载成功！")
        return file_path, filename


# 提取article
def get_article_node(html):
    selector = Selector(text=html)
    article_node = selector.xpath('//article[@class="movie-poster-card"]')
    for article in article_node:
        yield article


async def get_content(article):

    movie_list = []

    name = article.xpath('.//span[@class="movie-name-label cipher-title-text"]/text()').get()
    score_math = article.xpath('.//span[@class="movie-rating-badge cipher-number"]/text()').get()

    day = article.xpath('.//p[@class="movie-back-subtitle"]/text()').get()
    box_office = article.xpath(
        './/div[contains(@class,"movie-back-stat-wide")]//span[@class="movie-back-value cipher-number"]/text()').get()
    hot = article.xpath(
        './/div[span[text()="热度"]]//span[@class="movie-back-value cipher-number"]/text()').get()
    want = article.xpath(
        './/div[span[text()="想看"]]//span[@class="movie-back-value cipher-number"]/text()').get()

    mapping_path = "./font/mapping.json"
    data = {
        "影片名称": decrypt_text(mapping_path,name).strip() if name else "",
        "评分": to_float(decrypt_text(mapping_path,score_math.split()[0])) if score_math else "",
        "上映天数": decrypt_text(mapping_path,day) if day else "",
        "实时票房(亿)": to_float(decrypt_text(mapping_path,box_office)) if box_office else "",
        "热度(万)": to_float(decrypt_text(mapping_path,hot)) if hot else "",
        "想看(万)": to_float(decrypt_text(mapping_path,want)) if want else ""
    }

    return  data


async def main():
    moves_list = []
    # 1. 下载字体
    font_path, filename = download_font()
    if not font_path:
        print("字体下载失败，跳过")

    # 定义映射表路径和未确定字符目录
    mapping_path = font_path.replace(".woff2", ".mapping.json")
    unresolved_dir = font_path.replace(".woff2", "_unresolved")

    # 如果映射表不存在，则调用 PaddleOCR 生成
    if not os.path.exists(mapping_path):
        print(f"映射表不存在，开始构建: {mapping_path}")
        process_font_with_ddddocr(font_path, mapping_path, unresolved_dir)

    for html in get_html(base_url):
        for article in get_article_node(html):

            data = await get_content(article)

            moves_list.append(data)

    print(len(moves_list))

    base = max(moves_list, key=lambda x: x["实时票房(亿)"])
    print(base)

asyncio.run(main())