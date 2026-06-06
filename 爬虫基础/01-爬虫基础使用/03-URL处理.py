#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 谢泽华
# @Date: 2026/4/24 22:30
# @Desc:

from urllib.parse import urljoin

base = "https://example.com/a/b/c?x=1&b=2#hash"

print("相对路径：", urljoin(base, "img/1.jpg"))
# https://example.com/a/b/img/1.jpg

print("相对路径./：", urljoin(base, "./path"))
# https://example.com/a/b/path

print("相对路径../：",urljoin(base, "../css/main.css"))
# https://example.com/a/css/main.css

print("绝对路径：", urljoin(base, "/static/app.js"))
# https://example.com/static/app.js