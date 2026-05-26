#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 谢泽华
# @Date: 2026/5/3 16:40
# @Desc:

import requests
from parsel import Selector
import re
from urllib.parse import urljoin

# BASE_URL = 'http://5ys4lnu.haobachang1.loveli.com.cn:8888/search'
# HEADERS = {
#     "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
#     # "referer": "https://www.taobao.com/"
# }
#
# data  = {
#     "q":"qiansanyi"
# }
#
# response = requests.post(BASE_URL, data = data, headers=HEADERS)
#
# print(response.json())

# url = "http://hqr3jo7.haobachang1.loveli.com.cn:8888/flag"
# response = requests.get(url)
# print(response.text)

# url = "http://uiu5ax4.haobachang2.loveli.com.cn:8888/flag"
#
# data = {
#     "flag":1
# }
# response = requests.post(url, data=data)
# print(response.text)

# url = "http://55dx2t3.haobachang2.loveli.com.cn:8888/flag"
# data = {
#     "flag":1
# }
# headers = {
#     'User-Agent': 'mozilla/5.0 (windows nt 10.0; win64; x64; rv:143.0) gecko/20100101 firefox/143.0'
# }
#
# response = requests.post(url,data=data,headers=headers)
# print(response.text)

url = "http://j9hontn.haobachang2.loveli.com.cn:8888/flag"
data = {
    'flag':"1"
}

resp = requests.post(url,json=data)
print(resp.text)