#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 谢泽华
# @Date: 2026/3/25 19:08
# @Desc:

import requests
import base64
from urllib.parse import urlencode,unquote
from html import unescape


# response = requests.get('https://tc.xfei.tech/web/index.html')
# print(response.apparent_encoding)
# response.encoding = 'utf-8'
# print(response.status_code)
# print(response.text)

# base64解码
text= "ZmxhZ3toYW9iYWNoYW5nLWh1YW4teWluZy1uaW59"

bytes = base64.b64decode(text)
info = bytes.decode('UTF-8')
print(info)

# url解码
url = "%66%6c%61%67%7b%68%61%6f%62%61%63%68%61%6e%67%2d%68%75%61%6e%2d%79%69%6e%67%2d%6e%69%6e%5f%75%72%6c%64%65%63%6f%64%65%7d"
res = unquote(url)
print(res)

# HTML解码
html = "JiN4NjY7JiN4NmM7JiN4NjE7JiN4Njc7JiN4N2I7JiN4NjI7JiN4NjM7JiN4MzE7JiN4Mzk7JiN4MzY7JiN4MzA7JiN4NjI7JiN4NjI7JiN4Mzk7JiN4Mzg7JiN4MzQ7JiN4NjE7JiN4Mzk7JiN4NjM7JiN4MzI7JiN4MzE7JiN4NjE7JiN4MzQ7JiN4MzY7JiN4NjI7JiN4Mzk7JiN4MzA7JiN4MzY7JiN4MzI7JiN4NjQ7JiN4MzM7JiN4MzE7JiN4NjU7JiN4MzE7JiN4NjU7JiN4MzY7JiN4MzY7JiN4N2Q7"
bytes_html = base64.b64decode(html).decode('UTF-8')
print(bytes_html)
result = unescape(bytes_html)
print(result)

# HEX编码
test = "66 6c 61 67 7b 33 62 39 36 65 39 66 63 2d 61 65 35 34 2d 34 36 62 66 2d 39 65 33 30 2d 63 31 36 37 66 38 32 35 64 37 63 66 7d"
res = bytes.fromhex(test.replace(" ","")).decode()
print(res)

# Unicode编码
s = "flag{\u597D\u9776\u573A\u771F\u7684\u597D}"
print(s)
