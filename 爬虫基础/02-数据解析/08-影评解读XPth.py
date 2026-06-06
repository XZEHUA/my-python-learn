#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 谢泽华
# @Date: 2026/4/19 12:20
# @Desc:

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
keywords_list = ["剧情", "人物", "结局", "节奏", "剪辑", "配乐"]
keyword_pattern = re.compile('|'.join(keywords_list))

def clean_text(value,default = '-'):
    if value:
        return value.strip()
    return default

def to_int(value,default = 0):
    try:
        return int(value)
    except (TypeError,ValueError):
        return default

def hit_keywords(text):
    if not text:
        return set()
    return set(keyword_pattern.findall(text))

# 翻页
def iter_page_urls(total = 8):
    for page in range(1, total + 1):
        yield BASE_URL.format(page)

# 提取 li
def iter_lis(page_url):
        response = requests.get(page_url, headers=HEADERS)
        selector = Selector(text=response.text)
        reviews = selector.xpath("""
            //li[
                .//span[contains(@class,"allstar10")] 
                or
                number(
                    translate(
                        .//span[contains(@class,"reply-count")]/text(),
                        "💬 回应",""
                    )
                ) > 10
             ]
        """)

        for review in reviews:
            yield review

# 数据解析
def pares_review(review):
    # 完整评论
    review_id = review.attrib["data-review-id"]
    full_url = urljoin(BASE_URL, review_id)
    full_response = requests.get(full_url, headers=HEADERS)
    full_selector = Selector(text=full_response.json()['data']['body'])
    full_review = clean_text(''.join(
        full_selector.xpath('.//div[contains(@class,"review-content clearfix")]//text()').getall()
    ))
    if not hit_keywords(full_review):
        return None
    # 星级
    rating = clean_text(
        review.css('[class*="rating-allsta"]::attr(class)').get()
    ).split(' ')[-1].split('-')[0].split('allstar')[-1]
    # 用户名
    name = review.xpath('.//span[contains(@class,"author-name")]/text()').get()
    # 评论名
    title = review.xpath('.//h3[contains(@class,"review-title")]/text()').get()
    # 点赞
    useful_count = to_int(
        clean_text(
            review.xpath('.//span[contains(@class,"useful-count")]/text()').get()
        ).replace('👍', '')
    )
    # 点踩
    useless_count = to_int(
        clean_text(
            review.xpath('.//span[contains(@class,"useless-count")]/text()').get()
        ).replace('👎', '')
    )
    # 回应
    reply_count = to_int(
        clean_text(
            review.xpath('.//span[contains(@class,"reply-count")]/text()').get()
        ).replace('💬','').replace('回应','')
    )
    # reply_count = review.xpath('.//div/div/span[contains(@class,"reply-count")]/text()').get()

    data = {
        'review_id': review_id,
        'name': name,
        'title': title,
        'useful_count': useful_count,
        'useless_count': useless_count,
        'reply_count': reply_count,
        'full_review': full_review,
        'rating':rating,
    }
    return data

# 数据流
def data_stream():
    for page_url in iter_page_urls(total = 8):
        for review in iter_lis(page_url):
            data = pares_review(review)
            if data:
                yield data


def main():
    results = []
    total_useful = 0
    for idx,data in enumerate(data_stream(),1):
        results.append(data)
        total_useful += data['useful_count']
        print(f'{idx:>2}. [{data["rating"]} | 💬{data["reply_count"]} | 👍{data["useful_count"]} | title{data["title"]}]')
    print(f"共命中 {len(results)} 符合条件的评论，点赞总数{total_useful} 👍")

if __name__ == '__main__':
    main()




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
#             print(rating_class,type(rating_class))
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
#                 print(Long_review.url,Long_review.status_code)
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
#                 print(like1,like)
#
#
#                 sel2 = Selector(html_body)
#                 full_content = sel2.css("div.review-content"
#                                         ".clearfix::text").getall()
#                 full_content = "".join(full_content).strip()
#
#                 is_keywords = any(word in full_content for word in keywords_list)
#                 print(is_keywords)
#                 # any(word in full_content for word in keywords_list):
#                 if not is_keywords:
#
#                     continue
#
#                 total_like += like1
#                 print(f"评价：{rating} - 博主名：{username} - 评价标题：{title} - 回应数：{reply_num} - 点赞数：{like} - 点踩数：{dislike} - 是否包含关键字：{is_keywords}\n")
#
# print("答案为：",total_like,"\n")