#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 谢泽华
# @Date: 2026/3/25 19:19
# @Desc:

import requests
import time
from parsel import Selector

count = 0
for i in range(1, 11):
    url = f"https://movie.tc.xfei.tech/playground/movie-list-page/ZW82LI7LaccZ_yIeEdU/zh"
    params = {
        "page" : i,
        "size" : 25
    }
    response = requests.get(url, params=params)
    selector = Selector(response.text)
    items = selector.css('.movie-rating-count::text').getall()
    for item in items:
        count += int(item[:-3])
    time.sleep(0.5)
    print(f"第{i}页数据抓取成功！")
    print(f"第{i}页url地址：",response.url)

print(f"总评分人数为{count}")

