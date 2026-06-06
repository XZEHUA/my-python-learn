#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 谢泽华
# @Date: 2026/5/12 16:53
# @Desc:
import re
from itertools import count
from urllib.parse import urljoin

import requests
from parsel import Selector

BASE_URL = "https://tc.xfei.tech/playground/tech-review/ZW824nxNagkE_zlAAHs/zh/?p={}&rows=10"

HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}



# 题目描述
# 你将进入一个科技评测站点，页面包含多篇手机评测信息。
# 请编写爬虫逐页抓取评测数据，从文本中提取价格与评分，并按以下条件进行筛选：
#
# 价格 < 5000
# 评分 > 4.5
# 最终答案为：同时满足以上两项条件的文章数量。

# 转整数
def to_float(value,default=0):
    try:
        return float(value.replace(",",""))
    except (ValueError, TypeError):
        return default

# 转文本
def to_str(text):
    return str(text).strip()

def next_url(sel,current_url):
    next_href = sel.css(".pagination >a:last-child::attr(href)").get()
    print(next_href)

# 翻页
# def crawl_pagess(html):
#     sel = Selector(text=html)
#     next_page = sel.xpath("//div[contains(@class,'pagination')]/a[text()='下一页']").get()
#     if next_page:
#         sel2 = Selector(text=next_page)
#         next_url = sel2.xpath("//a/@href").get()
#         return next_url
#     else:
#         return None

def crawl_pages(total=5):
    for page in range(1,total+1):
        yield BASE_URL.format(page)


# 提取html
def get_html(url):
    response = requests.get(url, headers=HEADERS)
    return response.text

# 提取每页的 article
def clean_text(html):
    sel = Selector(text=html)
    articles = sel.css(".article-card")
    # next_url = crawl_pagess(html)
    return articles

# 提取名字
def get_name(article):
    name = article.css("div.author-info").re_first("作者：(.+? |$)")
    return name

# 提取评分
def get_rating(article):
    raticle = article.css("div.score-badge").re_first(r"\d.\d")
    return  to_float(raticle)

# 数据打包
def get_price(articles):
    data_list = []
    for article in articles:
        price_cn = to_float(article.css(".price-cn::text").re_first(r"[\d,.]+"))
        price_us = to_float(article.css(".price-us::text").re_first(r"[\d,.]+"))
        deal_price = to_float(article.css(".deal-price::text").re_first(r"[\d,.]+"))
        name = get_name(article)
        rating = get_rating(article)
        # print(price_cn,price_us,deal_price)

        data = {
            "name": name,
            "price_cn": price_cn,
           " price_us": price_us,
            "deal_price": deal_price,
            "rating": rating,
            # "url": next_url
        }
        data_list.append(data)
    return data_list

def main():
    total_cunte = 0
    for i in crawl_pages(total= 5):
        html = get_html(i)
        article = clean_text(html)
        for data in get_price(article):
            if data["price_cn"] < 5000 and data["rating"] > 4.5:
                total_cunte += 1
                print(total_cunte,data)
    print(total_cunte)




if __name__ == "__main__":
    main()