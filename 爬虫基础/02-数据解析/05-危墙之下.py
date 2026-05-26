#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 谢泽华
# @Date: 2026/3/25 23:33
# @Desc:

import requests
# import urllib3
# urllib3.disable_warnings()
import logging
logging.captureWarnings(True)
from parsel import Selector

# url = "https://ssl.tc.xfei.tech/playground/movie-list-ssl/ZW826XfXaccZ_7yv_xw/zh/"
# headers = {
#     'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36'
# }
# response = requests.get(url,headers=headers,verify=False)
# # print(response.text)
# selector = Selector(response.text)
# type_list = selector.css(".movie-genres::text").getall()
# new_type_list  =[]
# for t in type_list:
#     types = [i.strip() for i in t.split('/')]
#     new_type_list.extend(types)
# # print(type_list)
# # print(new_type_list)
# new_type_set = set(new_type_list)
# # print(new_type_set)
# print("答案为：",len(new_type_set))

url = "https://ssl.tc.xfei.tech/playground/movie-list-ssl/ZW826XfXadbr_3rOFcM/zh/"
headers = {
'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36'
}

response = requests.get(url, verify=False, headers=headers)

selector = Selector(response.text)
genres = selector.css(".movie-genres::text").getall()

data = set()
for i in genres:
    data.update(i.strip().split(" / "))
print(data)
print(len(data))