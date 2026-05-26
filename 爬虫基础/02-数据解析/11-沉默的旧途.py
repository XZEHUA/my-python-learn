#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 谢泽华
# @Date: 2026/5/15 02:21
# @Desc:

import httpx
from parsel import Selector

URL = "https://http2.tc.xfei.tech/playground/movie-list-http2/ZW822aoFagpWf68in7A/zh/"

HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def to_float(text):
    try:
        return float(text)
    except (ValueError,AttributeError):
        return text

data_list = []
with httpx.Client(http2=True) as client:
    response = client.get(url=URL, headers=HEADERS)
    selector = Selector(text=response.text)
    li_list = selector.xpath("//div/div/ul/li")
    for li in li_list:
        rating = to_float(li.xpath("./div[@class='movie-rating']/text()").get())
        movie_rank = li.xpath("./div[@class='movie-rank']/text()").get()
        data = {
            "rating": rating,
            "movie_rank": movie_rank
        }
        data_list.append(data)

best = max(data_list, key=lambda x: x["rating"])    # max(列表, key=lambda 每个元素: 按哪个字段比大小)

print("最高分电影：", best)
print("编号：", best["movie_rank"])


# 电影数据
movie_list = [
    {"rank": 1, "score": 9.5},
    {"rank": 2, "score": 8.2},
    {"rank": 3, "score": 7.6},
    {"rank": 4, "score": 8.8}
]

best_movie = movie_list[0]

for movie in movie_list:
    # 拿当前电影的评分 和 目前最高分比
    if movie["score"] < best_movie["score"]:
        # 如果更大，就替换掉
        best_movie = movie

# 3. 循环结束，best_movie 就是最高分
print("评分最高的电影：", best_movie)
print("电影编号：", best_movie["rank"])

base = min(movie_list, key=lambda x: x["score"])
print(base)


# 大数据比较
# 初始值
best_rating = -1
best_rank = None

with httpx.Client(http2=True) as client:
    response = client.get(url=URL, headers=HEADERS)
    selector = Selector(text=response.text)
    li_list = selector.xpath("//div/div/ul/li")

    for li in li_list:
        rating = to_float(li.xpath("./div[@class='movie-rating']/text()").get())
        movie_rank = li.xpath("./div[@class='movie-rank']/text()").get()

        # 直接比较，不保存所有数据
        if rating > best_rating:
            best_rating = rating
            best_rank = movie_rank

# 最后直接输出
print("最高分：", best_rating)
print("编号：", best_rank)