#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 谢泽华
# @Date: 2026/5/27 00:53
# @Desc: CSS 字体隐藏
import re

import requests
from parsel import Selector
from urllib.parse import urljoin
import asyncio

from playwright.async_api import async_playwright

BSEA_URL = "https://tc.xfei.tech/playground/css-content/ZW82xl-rahoof_EaJus/zh/"
HEADERS = {
    "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"
}


async def get_html(url):
    response = requests.get(url, headers=HEADERS)
    return response.text


async def get_css(html):
    selector = Selector(text=html)
    link = selector.xpath("//head/link[last()]/@href")
    link_href = str(link[0])
    css_url = urljoin(BSEA_URL, link_href)
    response = requests.get(url=css_url, headers=HEADERS)

    # 正则：匹配所有 .cipher-xxx::before{content:"x"}
    pattern = r'\.cipher-(\w+)::before\{content:"([^"]+)"\}'
    selector = Selector(text=response.text)
    cipher_map = dict(re.findall(pattern, response.text))
    return cipher_map


async def get_content(html, cipher_map):
    selector = Selector(text=html)
    result = []
    articles = selector.xpath('//article[contains(@class,"hotel-card")]')

    for article in articles:
        # 酒店名称
        title = article.xpath("./div/h3/text()").get()

        # 提取价格（price-track 内的 cipher）
        price_glyphs = article.xpath(
            './/div[@class="price-line"]'
            '//span[contains(@class,"cipher-glyph")]/@class'
        ).getall()
        chars = []
        for cls_str in price_glyphs:
            match = re.search(r'cipher-glyph cipher-(\w+)', cls_str)
            if match:
                key = match.group(1)
                chars.append(cipher_map.get(key, ''))
        real_price = ''.join(chars)

        # 提取评分（fact-grid 内第一个 fact-item）
        rating_glyphs = article.xpath(
            '(.//div[@class="fact-item"])[1]'
            '//span[contains(@class,"cipher-glyph")]/@class'
        ).getall()
        chars = []
        for cls_str in rating_glyphs:
            match = re.search(r'cipher-glyph cipher-(\w+)', cls_str)
            if match:
                key = match.group(1)
                chars.append(cipher_map.get(key, ''))
        rating = ''.join(chars)

        # 提取剩余房量（fact-grid 内第二个 fact-item）
        stock_glyphs = article.xpath(
            '(.//div[@class="fact-item"])[2]'
            '//span[contains(@class,"cipher-glyph")]/@class'
        ).getall()
        chars = []
        for cls_str in stock_glyphs:
            match = re.search(r'cipher-glyph cipher-(\w+)', cls_str)
            if match:
                key = match.group(1)
                chars.append(cipher_map.get(key, ''))
        stock = ''.join(chars)

        result.append({
            "title": title,
            "price": real_price,
            "rating": rating,
            "stock": stock,
        })

    return result


async def main():
    html = await get_html(BSEA_URL)
    cipher_map = await get_css(html)
    data = await get_content(html, cipher_map)
    print(data)

    # 打印所有酒店信息，方便查看
    print("=" * 60)
    print("所有酒店信息：")
    print("=" * 60)
    for item in data:
        print(f"酒店：{item['title']} | 价格：¥{item['price']} | 评分：{item['rating']} | 剩余房量：{item['stock']}间")

    # 筛选：评分 >= 4.7 且剩余房量 < 6
    filtered = []
    for item in data:
        try:
            rating = float(item['rating'])
            stock = int(item['stock'])
            price = float(item['price'])

            if rating >= 4.7 and stock < 6:
                filtered.append(item)
                print(
                    f"\n✓ 符合条件：{item['title']} | 价格：¥{item['price']} | 评分：{item['rating']} | 剩余房量：{item['stock']}间")
        except ValueError as e:
            print(f"✗ 数据转换失败：{item['title']} - {e}")
            continue

    print("\n" + "=" * 60)
    print(f"符合条件的房型数量：{len(filtered)}")

    # 计算总价
    total_price = sum(float(item['price']) for item in filtered)
    print(f"总价：¥{total_price:.2f}")
    print("=" * 60)

    return total_price


asyncio.run(main())
