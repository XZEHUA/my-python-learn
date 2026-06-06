#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 谢泽华
# @Date: 2026/3/29 18:41
# @Desc:

import requests
from parsel import Selector
from hashlib import md5
import urllib3
import time
from threading import Thread
from urllib.parse import urljoin

urllib3.disable_warnings()
found = False

# 配置
BASE_URL = "https://tc.xfei.tech/playground/wallpaper-list/ZW82Pg7oaf54_zlfUx0/zh/"
# TARGET_MD5 = "db21b4b735eed60c524b3df3d0863a0f"
TARGET_MD5 = "4c0b721f45dc76140ded2e25f1e47f8d"
HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "referer": "https://tc.xfei.tech/"
}


def get_img_4k(url):
    response = requests.get(url, headers=HEADERS)
    selector = Selector(response.text)
    img_4k = selector.css("div.download-bar a::attr(href)").getall()
    return img_4k[1]

def Turn_the_page():
    main_list = []
    start = 30
    for i in range(0, 10):
        params = {
            "start": start * i
        }
        resp = requests.get(BASE_URL,params=params, headers=HEADERS)
        selector = Selector(resp.text)
        img_urls = selector.css("#main-list .wallpaper-item:not(.ad-item) a::attr(href)").getall()
        main_list.extend(img_urls)
        # print(img_urls,len(img_urls))
    return main_list



if __name__ == "__main__":
    main_list =Turn_the_page()
    print(main_list,len(main_list))
    for img_url in main_list:
        url = urljoin(BASE_URL, img_url)
        img_4k_url = get_img_4k(url)
        img_4k = requests.get(img_4k_url, headers=HEADERS)
        img_md5 = md5(img_4k.content).hexdigest()
        if img_md5 == TARGET_MD5:
            print("找到了！url = %s" % url.split("/")[-1].split(".jpg"))
            break
        print("未找到目标！")
