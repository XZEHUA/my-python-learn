#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 谢泽华
# @Date: 2026/5/15 02:01
# @Desc:

import requests
from parsel import Selector

URL = "https://auth.tc.xfei.tech/playground/movie-list-auth/ZW82sxEragpWf58bT_c/zh/"

HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def to_float(text):
    try:
        return float(text)
    except (ValueError,AttributeError):
        return text

total = 0

response = requests.get(url=URL, headers=HEADERS,auth=("admin","admin"))
selector = Selector(text=response.text)
li_list = selector.xpath("//div/div/ul/li")
for li in li_list:
    rating = to_float(li.xpath("./div[@class='movie-rating']/text()").get())
    total += rating
    print(type(rating), rating)
print(total)