#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 谢泽华
# @Date: 2026/5/21 12:22
# @Desc:

import asyncio
import re
import pymongo
from playwright.async_api import async_playwright

client = pymongo.MongoClient("mongodb://crawler:crawler123@192.168.1.25:27017")
db = client.spiders # client["spiders"]
collection = db.movies_14 # db["movies_14"]

pipeline = [
    # 1. 数据清洗 ($match)
    # 确保年份字段存在，且不为空，防止统计到脏数据
    {
        "$match": {
            "上映年份": {"$exists": True, "$ne": None}
        }
    },

    # 2. 分组统计 ($group)
    {
        "$group": {
            "_id": "$上映年份",  # 按年份分组
            "count": {"$sum": 1}  # 计数，每遇到一部电影 +1
        }
    },

    # 3. 排序 ($sort)
    {"$sort": {"count": pymongo.DESCENDING}},  # 按数量倒序

    # 4. 限制 ($limit)
    {"$limit": 1}  # 只要第一名
]

result = list(collection.aggregate(pipeline))

if result:
    print(f"电影最多的年份: {result[0]['_id']}, 数量: {result[0]['count']}")
    print(f"答案为: {result[0]['_id']}-{result[0]['count']}")

print(collection.index_information())
