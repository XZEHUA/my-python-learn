#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 谢泽华
# @Date: 2026/5/6 16:27
# @Desc:
import threading

import requests
from parsel import Selector
import hashlib
import urllib3
import time
from urllib.parse import urljoin

urllib3.disable_warnings()


# 配置
BASE_URL = "https://tc.xfei.tech/playground/wallpaper-list/ZW82Pg7oaf54_zlfUx0/zh/"
TARGET_MD5 = "4c0b721f45dc76140ded2e25f1e47f8d"
HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "referer": "https://tc.xfei.tech/"
}

def my_get(url):
    try:
        response = requests.get(url, headers=HEADERS,timeout=5)
        response.raise_for_status()
        return response
    except requests.HTTPError as e:
        print('状态码异常：',e)
    except requests.RequestException as e:
        print("请求失败:",e)
    return None

# 翻页
def iter_page_urls(total=10, size=30 ):
    for i in range(total):
        yield f'https://tc.xfei.tech/playground/wallpaper-list/ZW82Pg7oaf54_zlfUx0/zh/?start={i*size}'

# 提取详情也 url
def iter_detail_urls(page_url):
    response = my_get(page_url)
    if not response:return
    selector = Selector(response.text)
    detail_paths = selector.css("#main-list .wallpaper-item:not(.ad-item) a::attr(href)").getall()
    for detail_path in detail_paths:
        yield urljoin(page_url, detail_path)

# 从详情也提取图片下载信息
def iter_image_info(detail_url):
    detail_response = my_get(detail_url)
    if not detail_response: return
    selector = Selector(detail_response.text)
    download_url = selector.css(".download-bar a:nth-of-type(2)::attr(href)").get()
    title = selector.css("h2::text").get()
    if download_url:

        yield {
            'download_url': download_url,
            'title': title,
            'detail_url': detail_url,
        }

# 图片信息流
def image_stream():
    for page_url in iter_page_urls():
        for detail_url in iter_detail_urls(page_url):
            yield from iter_image_info(detail_url)

# 判断是否命中
def is_target_image(image_dic):
    img_response = my_get(image_dic['download_url'])
    if not img_response:return False

    md5 = hashlib.md5(img_response.content).hexdigest()
    return md5 == TARGET_MD5

def main():
    for idx, image_dic in enumerate(image_stream(), start=1):
        print(f"正在处理第 {idx} 张图片")
        print('   标题：',image_dic['title'])
        print('   详情页：',image_dic['detail_url'])
        if is_target_image(image_dic):
            print("命中目标图片：",image_dic['detail_url'].split('/')[-1])
            break


if __name__ == "__main__":
    main()