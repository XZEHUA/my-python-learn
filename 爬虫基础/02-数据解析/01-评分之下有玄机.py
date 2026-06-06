#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 谢泽华
# @Date: 2026/3/25 19:11
# @Desc:

import requests

response = requests.get('https://movie.tc.xfei.tech/playground/movie-list/ZW82VQ6EaccZ_181St8/zh/')

print(response.status_code)
print(response.text)
print(response.headers)
print(len(response.text))
