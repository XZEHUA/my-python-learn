#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 谢泽华
# @Date: 2026/5/3 16:40
# @Desc:

import requests
from parsel import Selector
import re
from urllib.parse import urljoin

BASE_URL = 'https://www.taobao.com/'
HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "referer": "https://www.taobao.com/"
}

data  = {
    "q":"qiansanyi"
}

response = requests.post(BASE_URL, data = data, headers=HEADERS)

print(response.json())