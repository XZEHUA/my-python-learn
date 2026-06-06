#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 谢泽华
# @Date: 2026/5/21 12:22
# @Desc:



import requests


headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36',
}

params = {
    'limit': '10',
    'offset': '0',
    'token': 'ZjdhZDM1OTI5NDEzZDA5MmQ5MzlmNzllYWQ1ZDIwMjQwYjMwZmY5NywxNzc5MzM3NjI2',
}

response = requests.get(
    'https://tc.xfei.tech/playground/movie-list-ajax-token/ZW82KVoNahI_f4Qk11Y/zh/api/movies',
    params=params,
    headers=headers,
)

print(r'Status code:',response.status_code)
res = response.text
print(res)