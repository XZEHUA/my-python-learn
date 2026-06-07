#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 谢泽华
# @Date: 2026/6/5 18:15
# @Desc: 动态字体反爬 - 集成PaddleOCR (Python 3.10) 调用

import os
import requests
import asyncio
from urllib.parse import urljoin
from parsel import Selector
from font_ddddocr import process_font_with_ddddocr
import json
from hashlib import md5
from 爬虫基础.lib import decrypt_text

# 基础配置
BASE_URL = "https://tc.xfei.tech/playground/dynamic-font-map-novel/ZW820AdXaiYF_5VN09s/zh/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Python 3.10 环境配置
PY310_PYTHON = r"D:\Miniconda3\envs\paddle_gpu\python.exe"
# ocr_worker.py 的路径
WORKER_SCRIPT = os.path.join(os.path.dirname(__file__), r"E:\crawler\ocr_worker.py")

# 缓存目录
FONT_DIR = "./fonts2"
os.makedirs(FONT_DIR, exist_ok=True)


def get_title_url(url):
    """获取章节目录"""
    data_list = []
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"获取目录失败: {e}")
        return
    selector = Selector(text=response.text)
    articles = selector.xpath('//article[@class="chapter-list-item"]')
    for article in articles:
        title = article.xpath(".//h2/text()").get()
        href = article.xpath(".//a/@href").get()
        data_list.append({"title": title, "href": href})
    yield from data_list


def content_url(data):
    """拼接章节完整URL"""
    return urljoin(BASE_URL, data["href"])


def get_content(url):
    """获取单个章节的字体URL、标题和加密内容"""
    font_url = None
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"请求章节失败: {e}")
        return None, None, None
    selector = Selector(text=response.text)
    # 提取字体文件URL
    font = selector.xpath("//head/style/text()").re(r'src:\s*url\(["\']?(.*?)["\']?\)')
    if font:
        font_url = urljoin(BASE_URL, font[0])
    title = selector.xpath('//h1/text()').get()
    # 加密段落内容（只取最后一个p标签）
    text = selector.xpath('//article[@class="chapter-content cipher-copy"]/p[last()-1]/text()').get()
    if text:
        text = text.strip()
    return font_url, title, text


def download_font(font_url):
    """下载字体文件，返回本地路径和文件名"""
    if not font_url:
        return None, None
    filename = font_url.split("/")[-1]
    file_path = os.path.join(FONT_DIR, filename)
    if not os.path.exists(file_path):
        print(f"下载字体: {filename}")
        resp = requests.get(font_url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        with open(file_path, "wb") as f:
            f.write(resp.content)
    return file_path, filename


async def main():
    text = ""
    """主协程：遍历所有章节，解密内容"""
    for idx, data in enumerate(get_title_url(BASE_URL), start=1):
        print(f"\n===== 处理第 {idx} 章: {data['title']} =====")

        # 获取章节详情
        detail_url = content_url(data)
        font_url, title, encrypted_text = get_content(detail_url)
        if not font_url or not encrypted_text:
            print("跳过：字体URL或加密内容为空")
            continue

        # 下载字体
        font_path, filename = download_font(font_url)
        if not font_path:
            print("字体下载失败，跳过")
            continue

        # 定义映射表路径和未确定字符目录
        mapping_path = font_path.replace(".woff2", ".mapping.json")
        unresolved_dir = font_path.replace(".woff2", "_unresolved")

        # 如果映射表不存在，则调用 PaddleOCR 生成
        if not os.path.exists(mapping_path):
            print(f"映射表不存在，开始构建: {mapping_path}")
            success = process_font_with_ddddocr(font_path, mapping_path, unresolved_dir)

            if success:
                # 读取刚生成的映射表
                with open(mapping_path, 'r', encoding='utf-8') as f:
                    mapping = json.load(f)
                # 打印前10个映射
                print("映射表前10项:", list(mapping.items())[:10])
                # 提取加密文本中所有私有区字符的码点
                pua_codes = {hex(ord(ch)) for ch in encrypted_text if 0xE000 <= ord(ch) <= 0xF8FF}
                print("加密文本中私有区码点（前10个）:", list(pua_codes)[:10])
                # 检查交集
                overlap = set(mapping.keys()) & pua_codes
                print("映射表与加密文本共有的码点数量:", len(overlap))
                if overlap:
                    print("示例共有码点:", list(overlap)[:5])
                else:
                    print("警告：映射表与加密文本没有共同码点！解密将失败。")

            if not success:
                print("映射表构建失败，跳过此章节")
                continue
        else:
            print(f"使用已有映射表: {mapping_path}")

        # 解密文本
        try:
            plain_text = decrypt_text(mapping_path, encrypted_text)
            print(f"标题: {title}")
            print(f"解密后内容预览: {plain_text}")
            text += plain_text
            # 可以保存到文件或数据库
        except Exception as e:
            print(f"解密失败: {e}")
            continue


    text_md5 = md5(text.encode()).hexdigest()
    print(text_md5)

if __name__ == "__main__":
    asyncio.run(main())