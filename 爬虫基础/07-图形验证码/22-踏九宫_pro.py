#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 谢泽华
# @Date: 2026/6/30 16:53
# @Desc: 查询数据库，计算答案

from pymongo import MongoClient

MONGO_URI = "mongodb://crawler:crawler123@192.168.1.25:27017"
MONGO_DB = "spiders"
MONGO_COL = "Job_hunting_22"

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
collection = db[MONGO_COL]
hot_score = 0
items = collection.find()
for item in items:
    hot_score += item['hot_score']

print(hot_score)