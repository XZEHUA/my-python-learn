#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 谢泽华
# @Date: 2026/3/25 19:57
# @Desc:

import requests
from parsel import Selector

url = "https://tc.xfei.tech/playground/movie-list-ua/ZW82VQ6Eacxf_9jrVVY/zh/"
headers = {
'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36'
}

data = []
response = requests.get(url,headers=headers)
response.encoding = response.apparent_encoding
selector = Selector(response.text)

movies = selector.css(".movie-item")
for movie in movies:
    year = int(movie.css(".movie-details::text").get().strip()[:4])
    rating = int(movie.css(".movie-rating-count::text").get().strip()[:-3])
    title = movie.css(".movie-title::text").get().strip()
    info = {
        "year":year,
        "rating":rating,
        "title":title
    }
    data.append(info)

data.sort(key=lambda item: item["year"], reverse=True)
print(f"答案为：",data[0]['rating'])
