#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 谢泽华
# @Date: 2026/5/21 02:23
# @Desc:
import requests
from pymongo.collection import Collection
from typing import Any
import pymongo

BASE_URL = "https://tc.xfei.tech/playground/movie-list-ajax-infinite/ZW82XIyVahI_fwaSqgw/zh/api/movies"
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

PAGE_SIZE = 25
TOTAL_PAGES = 10
REQUEST_TIMEOUT = 10
MONGO_URL = "mongodb://root:1234@192.168.1.25:27017"
MONGO_DB = "spiders"
MONGO_COLLECTION = "ajax"

def fetch_page(page):
    params = {
        "limit": PAGE_SIZE,
        "offset": (page - 1) * PAGE_SIZE,
    }
    response = requests.get(url=BASE_URL, headers=headers, params=params, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.json().get("data",{}).get("movies",[])


def save_movies(collection: Collection[dict[str,Any]], movies: list[dict[str,Any]]) -> int:
    saved_count = 0
    for movie in movies:
        rank = movie.get("RankPosition")
        if rank is None:
            continue

        # 按 RankPosition 去重，存在则更新，不存在则插入
        res = collection.update_one({"RankPosition": rank},{"$set": movie}, upsert=True)
        if res.upserted_id is not None or res.modified_count > 0:
            saved_count += 1
    return saved_count

def crawl_and_save(collection: Collection[dict[str,Any]]):
    total_fetched = 0
    total_saved = 0

    for page in range(1,TOTAL_PAGES+1):
        movies = fetch_page(page)
        saved_count = save_movies(collection, movies)

        fetched_count = len(movies)
        total_fetched += fetched_count
        total_saved += saved_count
        print(f"[+] 第 {page:02d}页：抓取 {fetched_count} 条，写入/更新 {saved_count} 条")
    return total_fetched, total_saved

def main():
    # 连接 MongoDB
    client = pymongo.MongoClient(MONGO_URL)
    db = client[MONGO_DB]
    collection = db[MONGO_COLLECTION]

    try:
        total_fetched, total_count = crawl_and_save(collection)
        print(f"[+] 完成：共抓取 {total_fetched} 条，写入更新 {total_count} 条")

        movie = collection.find_one({},sort = [("RatingCount",pymongo.ASCENDING)])
        print("编号：",movie.get("RankPosition"))
        print("评分人数：",movie.get("RatingCount"))
    finally:
        client.close()


if __name__ == "__main__":
   main()