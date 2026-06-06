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
from 爬虫基础.lib import to_float
import decode_font



base_url = "https://tc.xfei.tech/playground/static-font-map/ZW82XxIIaiYF_3JRpp4/zh/"

HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"
}

if not os.path.exists('./font'):
    os.makedirs('./font')


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
def get_font(*url):
    if not url:
        url = "https://tc.xfei.tech/static/static-font-map/fonts/jiyun-cipher.woff2"
        HEADERS = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers = HEADERS)
        if os.path.exists("./font/jiyun-cipher.woff2"):
            print("字体文件已存在，跳过下载。")
            return True

        print("正在下载字体文件...")
        with open('./font/jiyun-cipher.woff2', 'wb') as f:
            f.write(response.content)
        print("字体下载成功！")
        return True


# 提取article
def get_article_node(html):
    selector = Selector(text=html)
    article_node = selector.xpath('//article[@class="movie-poster-card"]')
    for item in article_node:
        yield item


async def get_content(article_node):

    movie_list = []
    for item in article_node:
        name = item.xpath('.//span[@class="movie-name-label cipher-title-text"]/text()').get()
        score_math = item.xpath('.//span[@class="movie-rating-badge cipher-number"]/text()').get()

        day = item.xpath('.//p[@class="movie-back-subtitle"]/text()').get()
        box_office = item.xpath(
            './/div[contains(@class,"movie-back-stat-wide")]//span[@class="movie-back-value cipher-number"]/text()').get()
        hot = item.xpath(
            './/div[span[text()="热度"]]//span[@class="movie-back-value cipher-number"]/text()').get()
        want = item.xpath(
            './/div[span[text()="想看"]]//span[@class="movie-back-value cipher-number"]/text()').get()

        mapping_path = "./font/mapping.json"
        movie_list.append({
            "影片名称": decode_font.decrypt_text(mapping_path,name).strip() if name else "",
            "评分": to_float(decode_font.decrypt_text(mapping_path,score_math.split()[0])) if score_math else "",
            "上映天数": decode_font.decrypt_text(mapping_path,day) if day else "",
            "实时票房(亿)": to_float(decode_font.decrypt_text(mapping_path,box_office)) if box_office else "",
            "热度(万)": to_float(decode_font.decrypt_text(mapping_path,hot)) if hot else "",
            "想看(万)": to_float(decode_font.decrypt_text(mapping_path,want)) if want else ""
        })

    return  movie_list


async def main():
    moves_list = []
    # 1. 下载字体
    get_font()

    # 读取字体文件，创建映射表
    if not os.path.exists("./font/mapping.json"):
        decode_font.build_mapping_with_ddddocr("./font/jiyun-cipher.woff2", "./font/mapping.json")

    decode_font.merge_manual_mapping("./font/mapping.json", known_mapping={
        0xE07F: '.',
        0xE300: '·',
        0xE3d0: '!',
        0xE132: '1',
    })
    # 3. 获取页面并解析
    htmls = get_html(base_url)
    for html in htmls:
        article_nodes = get_article_node(html)
        movie_list = await get_content(article_nodes)
        for movie in movie_list:
            moves_list.append(movie)
            print(movie)


    print(len(moves_list))

    base = max(moves_list, key=lambda x: x["实时票房(亿)"])
    print(base)

asyncio.run(main())