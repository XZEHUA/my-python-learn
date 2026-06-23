#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 谢泽华
# @Date: 2026/6/15 08:54
# @Desc: Cookie 、接口分析
import asyncio
from urllib.parse import urljoin
from pymongo.errors import PyMongoError
from ocr_基础使用 import ocr_img
import aiohttp
from motor.motor_asyncio import AsyncIOMotorClient,AsyncIOMotorCollection



MONGO_URI = "mongodb://crawler:crawler123@192.168.1.25:27017"
MONGO_DB = "spiders"
MONGO_COL = "tenderin_20"


# 设置请求头，模拟 Chrome 浏览器，避免被识别为脚本。
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36',
}
API_URL = 'https://tc.xfei.tech/playground/tender-ocr/ZW829lyNaj3A_4OcDNI/zh/api/notices'
params = {}

# 获取数据
async def fetch_page(session, page, captcha_answer):
    """请求单页数据，返回 (items, new_captcha_url)"""
    params = {'page': page}
    if page == 1:
        params['force_captcha'] = '1'
    else:
        params['captcha_answer'] = captcha_answer

    async with session.get(API_URL, params=params, headers=headers) as resp:
        data = await resp.json()
        if not data.get('success'):
            print(f"第 {page} 页请求失败: {data.get('message')}")
            captcha_info = data['data'].get('captcha')
            img_url = captcha_info.get('image_url')
            return None, img_url

        items = data['data'].get('items', [])
        captcha_info = data['data'].get('captcha')
        img_url = captcha_info.get('image_url') if captcha_info else None
        return items, img_url


# 获取验证码
async def download_and_ocr(session, img_url):
    """下载验证码图片并识别"""
    full_url = urljoin('https://tc.xfei.tech', img_url)  # 或直接拼接
    async with session.get(full_url, headers=headers) as img_resp:
        img_data = await img_resp.read()
        return ocr_img(img_data)

# 创建数据库索引
async def create_indexes():
    motor_client = AsyncIOMotorClient(MONGO_URI)
    collection = motor_client[MONGO_DB][MONGO_COL]
    await collection.create_index("notice_id", unique=True)

# 数据存储
async def save_chapter_mongo(
    collection: AsyncIOMotorCollection,
    chapter: dict
):
    """异步入库：基于 notice_id 去重更新（upsert）"""
    await collection.update_one(
        {'notice_id': chapter['notice_id']},
        {'$set': chapter},
        upsert=True
    )
    print(f"已入库：{chapter['notice_id']}")

async def main():
    await create_indexes()
    page = 1  # 当前要抓取的页码，从第 1 页开始
    text = ''  # 用于存储上一次识别出的验证码答案（字符串），初次为空
    target = 0  # 计数器，记录满足条件（预算 > 1000 且状态为“招标中”）的公告数量
    motor_client = AsyncIOMotorClient(MONGO_URI)
    collection = motor_client[MONGO_DB][MONGO_COL]
    async with aiohttp.ClientSession() as session:
        while page <= 30:  # 可根据 total_pages 动态调整
            print(f"正在抓取第 {page} 页")
            items, img_url = await fetch_page(session, page, text)
            if items is None:
                # 请求失败，可尝试重试或跳过
                text = await download_and_ocr(session, img_url)
                continue
            # 处理数据
            for item in items:
                notice_id = item.get('notice_id')
                budget = item.get('budget_wan', 0)
                status = item.get('bid_status', '')
                if not notice_id:
                    continue
                if budget > 1000 and status == '招标中':
                    target += 1
                    try:
                        await save_chapter_mongo(collection, item)
                    except PyMongoError as e:
                        print(f"存储失败: {e}")
            # 获取下一页的验证码（如果有）
            if img_url:
                text = await download_and_ocr(session, img_url)
                print(f"识别验证码: {text}")
            else:
                text = ''  # 若没有验证码，清空

            page += 1

    print(f"满足条件的数据: {target}")

if __name__ == '__main__':
    asyncio.run(main())