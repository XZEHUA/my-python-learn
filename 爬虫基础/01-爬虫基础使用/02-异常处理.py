#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 谢泽华
# @Date: 2026/4/13 00:09
# @Desc:

import requests
from requests import ConnectTimeout

url = "https://tc.xfei.tech/test/404"

try:
    resp = requests.get(url,timeout=3)
    resp.raise_for_status()
    print(resp.status_code)
except requests.exceptions.Timeout as e:
    print("请求超时",e)
except requests.HTTPError as e:
    print("请求错误",e)
except requests.exceptions.RequestException as e:
    print(e)
else:
    print(resp.text)