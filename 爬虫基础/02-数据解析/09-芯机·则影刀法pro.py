#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 谢泽华
# @Date: 2026/5/12 16:53
# @Desc:

import re
import time
from itertools import count
from urllib.parse import urljoin
import requests
from parsel import Selector
import json

BASE_URL = "https://tc.xfei.tech/playground/tech-review/ZW824nxNagkE_zlAAHs/zh/"

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

def to_number(text):
    try:
        return float(text.replace(",", ""))
    except (ValueError,AttributeError) as e:
        print("转换失败 {e}")
        return None


def get_html(url):
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.text

# 场景1：标题提取
def s1_title(card):
    return card.css('.article-title::text').re_first(r"《(.+?)》")

# 场景2：数字提取
def s2_number(card):
    pattern = r"[\d,]+(?:\.\d+)?"
    price_cn = card.css('.price-cn::text').re_first(pattern)
    price_us = card.css('.price-us::text').re_first(pattern)
    deal_price = card.css('.deal-price::text').re_first(pattern)
    views = card.css('.views::text').re_first(pattern)
    comments = card.css('.comments::text').re_first(pattern)
    likes = card.css('.likes::text').re_first(pattern)
    score_badge = card.css('.score-badge::text').re_first(pattern)
    return {
        "price_cn": to_number(price_cn),
        "price_us": to_number(price_us),
        "deal_price": to_number(deal_price),
        "views": to_number(views),
        "comments": to_number(comments),
        "likes": to_number(likes),
        "score_badge": to_number(score_badge)
    }

# 场景3：作者与联系方式提取
def s3_author(card):
    name = card.css('.author-info ::text').re_first(r"作者：(.*?) ")
    phone = card.css('.author-info ::text').re_first(r"联系方式：(\d{3}-\d{4}-\d{4})")
    return {"name": name, "phone": phone}

# 场景4：链接路径 ID 提取
def s4_ids(card):
    return {
        "article_id": card.css("a.article-link::attr(href)").re_first(r"/article/(\d+)(?:\?|$)"),
        "product_id": card.css("a.product-link::attr(href)").re_first(r"/product/([\w-]+)(?:\?|$)"),
        "review_id": card.css("a.review-link::attr(href)").re_first(r"/review/([\w-]+)(?:\?|$)")
    }

# 场景5：样本编号提取
def s5_samples(card):
    return card.css('.order-list > li:nth-child(1)::text').re_first(r"[A-Z\d-]+")

# 场景6：Script 中 json 提取与解析
def s6_market(selector):
    data_json = selector.css("script::text").re_first(r"(?s)window\.__MARKET__\s*=\s*(\{.*?\})\s*;")
    try:
        data = json.loads(data_json)
        return data.get("channels")
    except (json.JSONDecodeError,AttributeError) as e:
        print(f"JSON 解析失败：{data_json}, 错误：{e}")
        return None

# 场景7：多节点文本提取
def s7_specs(card):
    return {
        "version-info": card.xpath("string(./div[@class='version-info'])").re_first(r"\d+\.\d+\.\d+"),
        "spec-detail": to_number(card.xpath("string(./div[@class='spec-detail'])").re_first(r"\d+(?:\.\d+)?")),
        "battery": to_number(card.xpath("string(./div[@class='battery'])").re_first(r"[\d,]+"))
    }

def next_url(selector,current_url):
    next_href = selector.css('.pagination > a:last-child::attr(href)').get()
    if not next_href:
        return None
    return urljoin(current_url, next_href)

def crawl_pages(start_url):
    visited = set()
    current_url = start_url
    page_num = 1
    while current_url:
        if current_url in visited:
            break
        visited.add(current_url)

        html = get_html(current_url)
        selector = Selector(text=html)
        cards = selector.css(".article-card")
        next_page = next_url(selector, current_url)
        yield {
            "page": page_num,
            "current_url": current_url,
            "card_count": len(cards),
            "cards": cards,
            "next_url": next_page
        }
        if not next_page:
            break
        page_num += 1
        current_url = next_page
        time.sleep(0.5)

def final_count(cards):
    number_list = (s2_number(card) for card in cards)
    return sum(1 for numbers in number_list
     if numbers["price_cn"] is not None
     and numbers["score_badge"] is not None
     and numbers["price_cn"] < 5000
     and numbers["score_badge"] > 4.5)

def main():
    html = get_html(BASE_URL)
    selector = Selector(text=html)
    cards = selector.css(".article-card")
    if not cards:
        print("未找到评测卡片，请检查选择器或 URL")
        return
    first_card = cards[0]

    print("\n=== 场景1：标题提取 ===")
    print(s1_title(first_card))

    print("\n=== 场景2：数字提取 ===")
    print(s2_number(first_card))

    print("\n=== 场景3：作者与联系方式提取 ===")
    print(s3_author(first_card))

    print("\n=== 场景4：链接路径 ID 提取 ===")
    print(s4_ids(first_card))

    print("\n=== 场景5：样本编号提取 ===")
    print(s5_samples(first_card))

    print("\n=== 场景6：Script 中 json 提取与解析 ===")
    print(s6_market(selector))

    print("\n=== 场景7：多节点文本提取 ===")
    print(s7_specs(first_card))

    print("\n=== 综合题 ===")
    total = 0
    for item in crawl_pages(BASE_URL):
        print(f"[第{item['page']}页，卡片数：{len(item['cards'])}]")
        print(f"当前页：{item['current_url']}")
        print(f"下一页：{item['next_url']}")
        total += final_count(item['cards'])
    print(total)

if __name__ == "__main__":
    main()