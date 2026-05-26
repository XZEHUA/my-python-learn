#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 谢泽华
# @Date: 2026/4/19 12:20
# @Desc:
from itertools import count

import requests
from parsel import Selector
import re
from urllib.parse import urljoin

BASE_URL = 'https://tc.xfei.tech/playground/movie-reviews/ZW82a4ROagO-_5omar8/zh/?p={}'
# full_url = 'https://tc.xfei.tech/playground/movie-reviews/ZW82a4ROagEb_2CZo60/zh/4931491'
HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "referer": "https://tc.xfei.tech/"
}

def clean_text(value,default = '-'):
    if value:
        return value.strip()
    return default

def to_int(value,default = 0):
    try:
        return int(value)
    except (TypeError,ValueError):
        return default

# 翻页
def iter_page_urls(total=8):
    for page in range(1,total+1):
        yield BASE_URL.format(page)

# 提取li
def iter_lis(page_url):
    response = requests.get(page_url, headers=HEADERS)
    selector = Selector(text=response.text)
    reviews = selector.css('li[class*="review-item"]')
    for review in reviews:
        yield review

# 解析数据
def pares_review(review):
    # for review in reviews:

    # 用户名
    name = review.css('[class*="author-name"]::text').get()
    # 星级
    rating = clean_text(
        review.css('[class*="rating-allsta"]::attr(class)').get()
    ).split(' ')[-1].split('-')[0].split('allstar')[-1]
    # 评论名
    title = review.css('h3::text').get()
    # 点赞
    useful_count = to_int(
        clean_text(
            review.css('[class*="useful-count"]::text').get()
        ).replace('👍', '')
    )
    # 点踩
    useless_count = to_int(
        clean_text(
            review.css('[class*="useless-count"]::text').get()
        ).replace('👎', '')
    )
    # 回应
    reply_count = to_int(
        clean_text(
            review.css('[class*="reply-count"]::text').get()
        ).replace('💬','').replace('回应','')
    )
    review_id = review.attrib["data-review-id"]
    if to_int(rating) == 10 or reply_count > 10:
        data = {
            'name': name,
            'rating': rating,
            'title': title,
            'useful_count': useful_count,
            'useless_count': useless_count,
            'reply_count': reply_count,
            'review_id': review_id,
        }


        return data

# 完整评论
def full_comment(data):
    if not data:
        return None
    review_id = data['review_id']
    if not review_id:
        return set()
    full_url = urljoin(BASE_URL, review_id)
    full_response = requests.get(full_url, headers=HEADERS)
    full_selector = Selector(text=full_response.json()['data']['body'])
    full_review = clean_text(''.join(
        full_selector.css('.review-content.clearfix *::text').getall()
    ))

    return full_review

# 关键词过滤
def review_comment(full_content):
    keywords_list = ["剧情", "人物", "结局", "节奏", "剪辑", "配乐"]
    keyword_pattern = re.compile('|'.join(keywords_list))
    if not full_content:
        return set()
    return set(keyword_pattern.findall(full_content))


if __name__ == '__main__':
    results = []
    total_useful = 0
    for page_url in iter_page_urls(8):
        for review in iter_lis(page_url):
            data = pares_review(review)
            comment =full_comment(data)
            if review_comment(comment):
                results.append(data)
                total_useful+=data['useful_count']
                print('='*80)
                print(results,total_useful,"\n")

    print(total_useful)



















# keywords_list = ["剧情", "人物", "结局", "节奏", "剪辑", "配乐"]
# total_like = 0
# for i in range(1,9):
#     params = {
#         "p":i
#     }
#     try:
#         resp = requests.get(BASE_URL,headers=HEADERS,params=params)
#         resp.raise_for_status()
#         selector = Selector(resp.text)
#         li_list = selector.css("li.review-item-a3f5d8b2")
#     except requests.exceptions.Timeout as e:
#         print("请求超时", e)
#     except requests.HTTPError as e:
#         print("请求错误", e)
#     except requests.exceptions.RequestException as e:
#         print(e)
#     else:
#         for li in li_list:
#             # rating_match = li.css("span.allstar10-q7r8s9t0").get()
#             rating_class = li.css("span.rating-allstar-9e8f7g6h::attr(class)").getall()
#             # print(rating_class,type(rating_class))
#             rating = li.css("span.rating-title-5h4g3f2e::text").get()
#             username = li.css("span.author-name-a8b9c2d3::text").get()
#             title = li.css("div.review-content-d8c7b6a5 "
#                            "h3.review-title-e3f4d5c6::text").get()
#             # 回应数
#             Response_Quantity = li.css("span.reply-count-x9y0z1a2b::text").get()
#             reply_match = re.search(r'\d+', Response_Quantity) if Response_Quantity else None
#             reply_num = int(reply_match.group()) if reply_match else 0
#
#             # 点赞数
#             Like1 = li.css("div.review-actions-k1l2m3n4 "
#                           "span.useful-count-q1w2e3r4t::text").get()
#             like_match1 = re.search(r'\d+', Like1) if Like1 else None
#             like1 = int(like_match1.group()) if like_match1 else 0
#
#
#             # 点踩数
#             Dislike = li.css("div.review-actions-k1l2m3n4 "
#                              "span.useless-count-s5t6u7v8w::text").get()
#             dislike_match = re.search(r'\d+', Dislike) if Dislike else None
#             dislike = int(dislike_match.group()) if dislike_match else 0
#
#
#
#             # print(f"评价：{rating} - 博主名：{username} - 评价标题：{title} - 回应数：{reply_num} - 点赞数：{like} - 点踩数：{dislike} ")
#
#             if not (("allstar10-q7r8s9t0" in rating_class) or (reply_num > 10)):
#                 continue
#
#             review_id = li.css("p.short-text-f7g8h9i0j::attr(data-review-id)").get()
#             if not review_id:
#                 continue
#
#             detail_url = urljoin(BASE_URL,review_id)
#
#             try:
#                 Long_review = requests.get(detail_url,headers=HEADERS)
#                 print(title,rating)
#             except requests.exceptions.Timeout as e:
#                 print("请求超时", e)
#             except requests.HTTPError as e:
#                 print("请求错误", e)
#             except requests.exceptions.RequestException as e:
#                 print(e)
#             else:
#
#                 json_data = Long_review.json()
#                 html_body = json_data.get("data",{}).get("body","")
#                 # print(html_body)
#                 sel2 = Selector(html_body)
#
#                 if not html_body:
#                     continue
#
#                 #从接口拿点赞数
#                 Like = sel2.css("button.btn.useful_count::text").get()
#                 like_match = re.search(r'\d+', Like) if Like else None
#                 like = int(like_match.group()) if like_match else 0
#
#                 # print(like1,like)
#
#
#                 sel2 = Selector(html_body)
#                 full_content = sel2.css("div.review-content"
#                                         ".clearfix::text").getall()
#                 full_content = "".join(full_content).strip()
#
#                 is_keywords = any(word in full_content for word in keywords_list)
#                 # print(is_keywords)
#                 # any(word in full_content for word in keywords_list):
#                 if not is_keywords:
#
#                     continue
#
#                 total_like += like1
#                 print(f"评价：{rating}  - 评价标题：{title} - 回应数：{reply_num} - 返回包点赞数：{like} - 页面点赞数{like1} - 点踩数：{dislike} - 是否包含关键字：{is_keywords}\n")
#
# print("答案为：",total_like,"\n")

