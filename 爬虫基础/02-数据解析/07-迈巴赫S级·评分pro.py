#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 谢泽华
# @Date: 2026/5/6 21:28
# @Desc:
import requests
from parsel import Selector
import time

BASE_URL = "https://tc.xfei.tech/playground/car-review/ZW82Ebapaf54_9A27QA/zh/?page={}"
start = 1
end = 19

headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36'
    }

# 清理文本
def clean_text(value):
    return (value or '-').strip()

# 安全转 float
def to_float(value, default=0.0):
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

# 解析单条评价
def parse_article(article):
    # 用户信息
    username = clean_text(
        article.css(' h2 > a::text').get()
    )
    car = clean_text(
        article.css(' h3::text').get()
    )

    info = article.css('aside > section > div > div:nth-child(2)')
    # 购车信息
    buy_car = clean_text(
        article.css('aside > section > div > div:nth-child(1) > span:nth-child(2)::text').get()
    )

    buy_data = clean_text(
        info.css(' div:nth-child(1) > p:nth-child(1)::text').get()
    )
    buy_location = clean_text(
        info.css(' div:nth-child(2) > p:nth-child(1)::text').get()
    )
    buy_price = clean_text(
        info.css(' div:nth-child(3) > p:nth-child(1)::text').get()
    )
    buy_rang = clean_text(
        info.css(' div:nth-child(4) > p:nth-child(1)::text').get()
    )

    # 评分
    scores = {}
    for score in article.css('aside > section > div > div:nth-child(3) > div'):
        key = score.css('p:nth-child(2)::text').get()
        value = score.css('p:nth-child(1) > span > span.tw-relative::text').get()
        scores[key] = to_float(value)

    # 点评车型
    review_car = clean_text(
        article.css('h2 > span:nth-child(2)::text').get()
    )

    # 点评图片
    imgs = article.css('section > div.jsx-3125371293.tw-mt-12 > div > div > div > img.review-image::attr(src)').getall()
    return {
        'username': username,
        'car': car,
        'buy_car': buy_car,
        'buy_data': buy_data,
        'buy_location': buy_location,
        'buy_price': buy_price,
        'buy_rang': buy_rang,
        'scores': scores,
        'review_car': review_car,
        'imgs': imgs,
    }

# 计算答案
def calc_answer(reviews):
    # 点评数量 - 点评图片数量 - 购买数量 - 购买地点数量 - 评分平均值（保留 1 位小数）
    review_count = len(reviews)
    img_count = sum([len(item['imgs'])for item in reviews])
    buy_count = sum( 1 for item in reviews if item['buy_car'] != '-')
    ads_count = len({item['buy_location'] for item in reviews if item['buy_location'] != '-'})
    total_score = sum(scores for item in reviews for scores in item['scores'].values())
    scores_count = sum(len(item['scores']) for item in reviews)
    print(review_count, img_count, buy_count, ads_count, round(total_score/scores_count,1))

def main():
    all_reviews = []
    for i in range(start, end+1):
        url = BASE_URL.format(i)
        print(f'正在爬取第{i}页：{url}')
        try:
            response = requests.get(url, headers=headers,timeout=5)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f'第 {i} 页请求失败：{e}')
            continue
        selector = Selector(response.text)
        articles = selector.css(".new-main > div > section > section:nth-child(1) > article")
        for article in articles:
            # 解析单条评价
            all_reviews.append(parse_article(article))
        print(f'第 {i} 页爬取完成，当前数据量{len(all_reviews)}')
        time.sleep(0.5)
    calc_answer(all_reviews)


if __name__ == '__main__':
    main()

