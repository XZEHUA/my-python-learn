#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 谢泽华
# @Date: 2026/5/27 00:19
# @Desc: CSS 偏移反爬

import requests
from parsel import Selector
import re
import asyncio

BASE_URL = 'https://tc.xfei.tech/playground/css-offset/ZW82GbTIahoof5Lkfcs/zh/'
HEADERS = {
    "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"
}


async def parse_title(article_node):
    """
    解析标题，兼容 CSS 偏移反爬和正常标题两种情况

    Args:
        article_node: article 节点的 HTML 字符串 或 parsel Selector 对象

    Returns:
        str: 解析后的标题文本
    """
    if isinstance(article_node, str):
        sel = Selector(text=article_node)
        article_node = sel.css('article.item') or sel

    # 定位标题 h3 节点
    title_h3 = article_node.css('h3.item-title')
    if not title_h3:
        return ''

    # 查找是否包含 char 类的 span（CSS 偏移反爬特征）
    char_spans = title_h3.css('span.char')

    if char_spans:
        # 情况1：CSS 偏移反爬，按 left 值排序后拼接
        def extract_left_px(span):
            """从 style 中提取 left 的像素值，用于排序"""
            style = span.css('::attr(style)').get('')
            match = re.search(r'left:\s*(\d+(?:\.\d+)?)\s*px', style)
            return  float(match.group(1)) if match else float('inf')

        # 按 left 值从小到大排序
        sorted_spans = sorted(char_spans, key= extract_left_px)
        # 拼接文本
        title = ''.join(span.css('::text').get('').strip() for span in sorted_spans)
        return title
    else:
        # 情况2：正常标题，直接取文本
        text_list = title_h3.css('::text').getall()
        title = ''.join(t.strip() for t in text_list if t.strip())
        return title


async def parse_price(article_node):
    if isinstance(article_node, str):
        sel = Selector(text=article_node)
        article_node = sel.css('article.item') or sel
    # 1. 在当前 article_node 内部找（用 ./ 或 .//）
    price_div = article_node.xpath('./aside/div/div[contains(@class,"digit-track")]')
    if not price_div:
        return ''

    # 2. 重点：在 price_div 内部找 span，必须用 .// 开头
    spans = price_div.xpath('.//span[contains(@class,"digit")]')

    digits = []
    for span in spans:
        # 提取 order
        order_str = span.xpath('substring-before(substring-after(@style, "--glyph-order: "), ";")').get()
        if not order_str:
            continue
        order = int(order_str.strip())
        # 提取字符
        char = span.xpath('text()').get()
        if char is None:
            char = ''
        digits.append((order, char.strip()))

    # 按 order 排序后拼接
    digits_sorted = sorted(digits, key=lambda x: x[0])
    price_str = ''.join(d for _, d in digits_sorted)

    return price_str

async def get_article_node(url):
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
    except requests.exceptions.Timeout as e:
        print("请求超时", e)
    except requests.HTTPError as e:
        print("请求错误", e)
    except requests.exceptions.RequestException as e:
        print(e)
    else:
        sel = Selector(text=response.text)
        article_node = sel.xpath('//main/section/div[contains(@class,"list-wrap")]/article')
        return article_node

async def main():
    data_list = []
    article_node = await get_article_node(BASE_URL)
    for item in article_node:
        title = await parse_title(item)
        price = await parse_price(item)
        data = {
            'title': title,
            'price': price,
        }
        data_list.append(data)

    # 1. 按价格从低到高排序
    sorted_items = sorted(data_list, key=lambda x: float(x['price']))

    # 2. 取出前3个标题
    top3_names = [item['title'] for item in sorted_items[:3]]

    # 3. 用逗号连接输出（你要的格式）
    result = ",".join(top3_names)

    # 打印最终结果
    print(result)



asyncio.run(main())