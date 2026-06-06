#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 谢泽华
# @Date: 2026/5/15 12:36
# @Desc:

import requests
from parsel import Selector
import pymysql
#
# conn = pymysql.connect(host="192.168.1.89",user="root",passwd="Root@123",port=3306)
# cursor = conn.cursor()
# cursor.execute("SELECT VERSION()")
# data = cursor.fetchone()
# print(data)
# cursor.execute("CREATE DATABASE IF NOT EXISTS spiders")
# cursor.execute("USE spiders")
# cursor.close()
# conn.close()


# 建表
import pymysql

conn = pymysql.connect(host="192.168.1.25",user="crewler_user",passwd="Mysql1234@",port=3306,db="spiders")
cursor = conn.cursor()
sql = """
CREATE TABLE IF NOT EXISTS movies (
    id INT NOT NULL AUTO_INCREMENT primary key,
    movie_id INT NOT NULL unique,
    title VARCHAR(255) NOT NULL,
    genres VARCHAR(255) NOT NULL,
    rating FLOAT
);
"""

# sql = """
# drop table movies;
# """

cursor.execute(sql)
cursor.close()
conn.close()





URL = "https://movie.tc.xfei.tech/playground/movie-list/ZW82VQ6Eag5K_xhZXqU/zh/"

response = requests.get(URL)
selector = Selector(response.text)
items = selector.xpath("//div/div/ul/li")

for item in items:
    title = item.xpath("./div/div[@class='movie-title']/text()").get()
    movie_genres = item.xpath("./div/div[@class='movie-genres']/text()").get()
    movie_rating = item.xpath("./div[@class='movie-rating']/text()").get()
    movie_id = item.xpath("./div [@class='movie-rank']/text()").get()
    if not title:
        continue
    data = {
        "movie_id": movie_id,
        "title": title,
        "genres": movie_genres,
        "rating": movie_rating
    }
    print(data)


# 插入
# id= 1
# title= "肖申克的救赎"
# rating= 9.6
#
# conn = pymysql.connect(host="192.168.1.25",user="crewler_user",passwd="Mysql1234@",port=3306,db="spiders")
# cursor = conn.cursor()
# sql = f"""
# insert into movies (id,title,rating) values (%s,%s,%s) on duplicate key update title = values(title),rating = values(rating) ;
# """
# try:
#     cursor.execute(sql,(id,title,rating))
#     print("成功")
#     conn.commit()
# except:
#     print("失败，回滚")
#     conn.rollback()
# cursor.close()
# conn.close()
#

# 跟新
# conn = pymysql.connect(host="192.168.1.25",user="crewler_user",passwd="Mysql1234@",port=3306,db="spiders")
# cursor = conn.cursor()
# sql = """
# update movies set rating = %s where id = %s
# """
# try:
#     cursor.execute(sql,(9.6,1))
#     print("成功")
#     conn.commit()
# except:
#     print("失败，回滚")
#     conn.rollback()
# cursor.close()
# conn.close()

# 字典
# data = {
#     "id": 3,
#     "title": "泰坦尼克号",
#     "rating": 9.5
#     }
#
    keys = list(data.keys())
    values = list(data.values())

    keys_str = ",".join(keys)
    value_placeholder = ','.join(['%s'] * len(values))

    update_keys = [k for k in keys if k != "movie_id"]
    update_srt = ','.join(f'{k} = values({k})' for k in update_keys)

    conn = pymysql.connect(host="192.168.1.25",user="crewler_user",passwd="Mysql1234@",port=3306,db="spiders")
    cursor = conn.cursor()
    sql = f"""
    insert into movies ({keys_str}) values ({value_placeholder}) on duplicate key update {update_srt} ;
    """
    try:
        cursor.execute(sql,values)
        print("成功")
        conn.commit()
    except:
        print("失败，回滚")
        conn.rollback()

cursor.close()
conn.close()


# 删除
# table = "movies"
# condition = "rating < 9.8"
#
# conn = pymysql.connect(host="192.168.1.25",user="crewler_user",passwd="Mysql1234@",port=3306,db="spiders")
# cursor = conn.cursor()
# sql = f"""
# delete from {table} where {condition};
# """
# try:
#     cursor.execute(sql)
#     print("成功")
#     conn.commit()
# except:
#     print("失败，回滚")
#     conn.rollback()
# cursor.close()
# conn.close()

# 查询
table = "movies"
condition = "rating > 9.0"

conn = pymysql.connect(host="192.168.1.25",user="crewler_user",passwd="Mysql1234@",port=3306,db="spiders")
cursor = conn.cursor(pymysql.cursors.DictCursor)
sql = f"""
select * from {table} where {condition};
"""
try:
    cursor.execute(sql)
    print("数量：", cursor.rowcount)
    # print("第一条：", cursor.fetchone())
    # print("全部：", cursor.fetchall())
    # for item in cursor.fetchall():
    #     print(item)
    row = cursor.fetchone()
    while row:
        print(row)
        row = cursor.fetchone()
except:
    print("失败")
cursor.close()
conn.close()