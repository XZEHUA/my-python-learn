#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 谢泽华
# @Date: 2026/5/15 12:36
# @Desc:

import requests
from parsel import Selector
import json
import csv

URL = "https://movie.tc.xfei.tech/playground/movie-list/ZW82VQ6Eag5K_xhZXqU/zh/"

response = requests.get(URL)
selector = Selector(response.text)
items = selector.xpath("//div/div/ul/li")

# txt
with open('01-评分之下有玄机.json', 'w', encoding='utf-8') as f:
    for item in items:
        title = item.xpath("./div/div[@class='movie-title']/text()").get()
        movie_genres = item.xpath("./div/div[@class='movie-genres']/text()").get()
        movie_rating = item.xpath("./div[@class='movie-rating']/text()").get()
        f.write(f"电影：{title} \n")
        f.write(f"类型：{movie_genres} \n")
        f.write(f"评分：{movie_rating} \n")
        f.write("============================================\n")

# 读取
# with open('01-评分之下有玄机.json', 'r', encoding='utf-8') as f:
#     res = f.read()
#     print(res)

# json
with open('01-评分之下有玄机.json', 'w', encoding='utf-8') as f:
    f.write("[\n")
    first = True
    for item in items:
        title = item.xpath("./div/div[@class='movie-title']/text()").get()
        movie_genres = item.xpath("./div/div[@class='movie-genres']/text()").get()
        movie_rating = item.xpath("./div[@class='movie-rating']/text()").get()
        if not first:
            f.write(",\n")
        first = False
        data = {
            "title": title,
            "genres": movie_genres,
            "rating": movie_rating
        }
        json.dump(data, f,indent=2, ensure_ascii=False)
    f.write("\n]\n")

# json 读取
# with open('01-评分之下有玄机.json', 'r', encoding='utf-8') as f:
#     data_list = json.load(f)
#     for item in data_list:
#         print(item)


# csv
with open("01-评分之下有玄机.csv", "w", encoding='utf-8',newline="") as f:
    writer = csv.DictWriter(f,fieldnames=["title","genres","rating"])
    writer.writeheader()
    for item in items:
        title = item.css(".movie-title::text").get()
        movie_genres = item.css(".movie-genres::text").get()
        movie_rating = item.css(".movie-rating::text").get()
        if not title:
            continue
        writer.writerow({"title": title, "genres": movie_genres, "rating": movie_rating})


# 读取 csv
# with open("01-评分之下有玄机.csv","r",encoding="utf-8") as f:
#     for row in csv.reader(f):
#         print(row)