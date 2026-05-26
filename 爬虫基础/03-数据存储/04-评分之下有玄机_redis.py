#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 谢泽华
# @Date: 2026/5/18 23:01
# @Desc:

from redis import Redis

# redis = Redis(host='192.168.1.89', port=6379, db=0, password=123456)
redis = Redis.from_url('redis://:1234@192.168.1.25:6379/0', decode_responses=True)
# redis.set('name','hua')
# print(redis.get('name'))

# 列表
# redis.rpush('list',1,2,3)
# redis.lpush('list',4,5,6)
# print(redis.lrange('list',0,-1))

# 集合
# redis.sadd('set',1,2,3,4,5)
# print(redis.smembers('set'))

# 有序集合
# redis.zadd('zset',{'a':1,'b':2,'c':3,'d':4,'e':5})
# print(redis.zrange('zset',0,2))
# print(redis.zrevrange('zset',0,2))

# Hash (散列) 类似 python 字典
redis.hset('dict',mapping={'name':'hua','age':18})
redis.hset('dict','gender','male')
print(redis.hget('dict','name'))
print(redis.hgetall('dict'))