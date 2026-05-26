#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 谢泽华
# @Date: 2026/5/21 00:51
# @Desc:

from elasticsearch import Elasticsearch

es = Elasticsearch('http://192.168.1.25:9200')  # basic_auth=('admin', '123456')

# data = {
#     "title": '人工智能爆发：人工智能将重塑未来，人工智能将无处不在',
#     "content": "人工智能技术正在飞速发展。专家认为，人工智能不仅仅是工具，人工智能更是未来的基石,逐步渗透到医疗、教育、交通、金融、工业制造等各个领域。专家认为，人工智能不仅仅是高效工具，更是驱动数字经济与社会进步的核心力量。未来，人工智能将实现更深度的场景落地，从智能家居到自动驾驶，从智能诊断到产业自动化，人工智能将全面融入日常生活，成为推动世界变革的关键技术。。",
#     "author": "张三",
#     "category": "科技",
#     "published_at": '2026-03-12T10:00:00',
#     "view_count": 5000,
#     "is_breaking": True
# }
#
# res = es.index(index='news',id='1',document=data)
# print(res)

# index_to_delete = 'news'
#
# # 先检查索引是否存在，避免报错
# if es.indices.exists(index= index_to_delete):
#     try:
#         es.indices.delete(index= index_to_delete)
#         print(f"索引'{index_to_delete}'已成功删除")
#     except Exception as e:
#         print(f"删除索引是发生错误：{e}")
# else:
#     print(f"索引 '{index_to_delete}' 不存在，无需删除")


index_name = "news_articles"
#
# # 定义新闻数据的映射结构
# mapping = {
#     "mappings": {
#         "properties": {
#             "title": {"type": "text", "analyzer": "ik_max_word", "search_analyzer": "ik_smart"},      # 标题，需分词，写入时使用 ik_max_word（切分得最细，利于被搜到），而在搜索时使用 ik_smart（切分得较粗，利于匹配长词，减少误判）。
#             "content": {"type": "text", "analyzer": "ik_max_word", "search_analyzer": "ik_smart"},    # 正文，需分词，写入时使用 ik_max_word（切分得最细，利于被搜到），而在搜索时使用 ik_smart（切分得较粗，利于匹配长词，减少误判）。
#             "author": {"type": "keyword"},                          # 作者，精确匹配
#             "category": {"type": "keyword"},                        # 分类 (如: 科技, 体育)
#             "published_at": {"type": "date"},                       # 发布时间
#             "view_count": {"type": "integer"},                      # 阅读量
#             "is_breaking": {"type": "boolean"}                      # 是否突发新闻
#         }
#     }
# }
#
# # 如果索引不存在则创建
# if not es.indices.exists(index=index_name):
#     es.indices.create(index=index_name, body=mapping)
#     print(f"索引 '{index_name}' 创建成功")
# else:
#     print(f"索引 '{index_name}' 已存在")
#
#
#
# news_list = [
#     {
#         "title": "人工智能爆发：人工智能将重塑未来，人工智能无处不在",
#         "content": "人工智能技术正在飞速发展。专家认为，人工智能不仅仅是工具，人工智能更是未来的基石。随着人工智能算法的优化，人工智能的应用场景无处不在。人工智能、人工智能、人工智能，这就是当下的趋势。",
#         "author": "张三",
#         "category": "科技",
#         "published_at": "2026-03-12T10:00:00",
#         "view_count": 5000,
#         "is_breaking": True
#     },
#     {
#         "title": "最新报告：人工智能市场规模翻倍",
#         "content": "今日发布的行业白皮书指出，人工智能领域投资增长迅猛。许多公司开始布局人工智能赛道，人工智能人才缺口巨大。未来五年，人工智能将成为经济增长的新引擎。",
#         "author": "李四",
#         "category": "财经",
#         "published_at": "2026-03-12T11:00:00",
#         "view_count": 3200,
#         "is_breaking": False
#     },
#     {
#         "title": "某科技巨头发布全新战略计划",
#         "content": "该公司宣布将全面转型，重点投入人工智能研发。虽然面临挑战，但他们坚信人工智能能带来突破。此次战略调整标志着其正式进军人工智能深水区。",
#         "author": "王五",
#         "category": "科技",
#         "published_at": "2026-03-12T12:00:00",
#         "view_count": 1800,
#         "is_breaking": False
#     },
#     {
#         "title": "机器人大会开幕，展示人工智能成果",
#         "content": "本次大会展示了各种先进的机器人技术，其中也包括了一些基础的人工智能应用演示，吸引了大量观众围观。",
#         "author": "赵六",
#         "category": "科技",
#         "published_at": "2026-03-12T13:00:00",
#         "view_count": 900,
#         "is_breaking": False
#     },
#     {
#         "title": "大数据时代下的隐私保护挑战",
#         "content": "随着数据采集能力的提升，大数据的应用越来越广泛。如何在大数据环境中保护用户隐私，成为了亟待解决的问题。大数据技术本身是中立的。",
#         "author": "孙七",
#         "category": "法律",
#         "published_at": "2026-03-12T14:00:00",
#         "view_count": 1200,
#         "is_breaking": False
#     }
# ]
#
# # 批量插入
# print("--- 正在插入数据 ---")
# for i, doc in enumerate(news_list):
#     resp = es.index(index=index_name, document=doc)
#     print(f"[{i+1}] 插入成功: {doc['title'][:15]}...")


# 查询
query = {
    "query": {
        "match": {
            "content": "人工智能 机器人"
        }
    }
}

response = es.search(index=index_name, body=query)

# 处理结果
hits = response['hits']['hits']
print(f"找到 {len(hits)} 篇相关新闻")
for hit in hits:
    source = hit['_source']
    print(f"[{source['category']}] {source['title']} (作者: {source['author']})")
    print(f"{source['content']}")
    print("\n","="*150)