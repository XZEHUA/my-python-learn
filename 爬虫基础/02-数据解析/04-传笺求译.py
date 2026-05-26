#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 谢泽华
# @Date: 2026/3/25 23:13
# @Desc:
from sqlite3.dbapi2 import paramstyle

import requests

# url = 'https://tc.xfei.tech/playground/trans-text-post/ZW82l4H7accZ_zZuytI/zh/'
# headers = {
#     'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
#     # "Content-type":"application/x-www-form-urlencoded",
#     # "Referer":"https://tc.xfei.tech/playground/trans-text-post/ZW82l4H7accZ_zZuytI/zh/"
# }
# data = {
#     "kw":"text"
# }
# api_url = url + "sug"
# response = requests.post(api_url,data=data, headers = headers)
# response.encoding = response.apparent_encoding
# if response.status_code == 200:
#     print("答案为：", response.json()["answer"])


# 文件上传
url = "https://tc.xfei.tech/playground/trans-text-post/ZW82l4H7adbr_yKM9xU/zh/upload"

headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
}

# data = {
#     'file':open("04-test",'rb',)
# }
data = [
    ('file',open('04-test', 'rb')),
    ('file',open('04-test', 'rb'))
]

response = requests.post(url,files=data,headers=headers)
dic = response.json()
print(dic)