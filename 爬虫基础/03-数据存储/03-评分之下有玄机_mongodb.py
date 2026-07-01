#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 谢泽华
# @Date: 2026/5/18 21:30
# @Desc:

import pymongo
from bson import ObjectId

client = pymongo.MongoClient("mongodb://crawler:crawler123@192.168.1.25:27017")
db = client.spiders # client["spiders"]
collection = db.tenderin_20 # db["movies"]

movie1 = {
    "id":1,
    "title":"肖申克的救赎",
    "rating":9.7
}

movie2 = {
    "id":2,
    "title":"霸王别姬",
    "rating":9.6
}
movie3 = {
    "id":1,
    "title":"泰坦尼克号",
    "rating":9.5
}

# 插入数据
# 单条
# res = collection.insert_one(movie1)
# print(res)
# print(res.inserted_id,res.acknowledged)
# # 多条
# res = collection.insert_many([movie2,movie3])
# print(res.inserted_ids)
# print(res.inserted_ids,res.acknowledged)

# 查
# res = collection.find_one({'id': 1})
# print(res)
# res = collection.find_one({'_id':ObjectId('6a0dce0b2d3e67034dd5053c')})
# print(res)
# res = collection.find_one({'title':'肖申克的救赎'})
# print(res)
# 查多条
# res = collection.find({'title':'肖申克的救赎'})
# print(res.next())
# 条件查询
# res = collection.find({'rating':{'$gt': 9}})
# # print(res.next())
# # print(res.next())
# # print(res.next())
# # print(res.next())
# for item in res:
#     print(item)
# 查所有,排序
# res = collection.find({}).sort({"rating": -1,"title":1})
# for item in res:
#     print(item)
# 跳过前面几条 .skip(1)
# res = collection.find({}).sort({"rating": -1,"title":1}).skip(1)
# for item in res:
#     print(item)
#取几条
# res = collection.find({}).sort({"rating": -1,"title":1}).skip(1).limit(2)
# for item in res:
#     print(item)
# 多数据查询
# res = collection.find({"_id":{'$gt':ObjectId("6a0b17786e4d4e417f593a92")}}).limit(2)
# for item in res:
#     print(item)
# 查数量
# res = collection.count_documents({})
# print(res)

# 更新数据
# res = collection.update_one({'id':1}, {'$set':{'rating':9.8}})
# print(res)
# print(res.matched_count,res.modified_count)
# 批量更新
# res = collection.update_many({'rating':{'$gt':9}}, {'$inc':{'rating':-1}})
# print(res)
# print(res.matched_count,res.modified_count)
# res = collection.find({})
# for item in res:
#     print(item)


# 删除
# collection.delete_one({'_id':ObjectId('6a0b175094af2a6a2bbbf6fd')})
# collection.delete_many({'rating':{'$gt':9}})