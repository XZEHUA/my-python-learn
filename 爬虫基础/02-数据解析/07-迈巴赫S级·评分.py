#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 谢泽华
# @Date: 2026/4/13 00:43
# @Desc:

import re
import requests
from parsel import Selector
import time

count = 0
total_images = 0
Purchase_Quantity = 0
Place_list = set()
Overall_score = []
Appearance_Score = []
interior = []
Configuration = []
space = []
Comfort = []
Control = []
score = []
avg = 0

for i in range(1,20):
    url = "https://tc.xfei.tech/playground/car-review/ZW82Ebapaf_Kf02Q5LQ/zh/"
    params = {
        "page" : i,
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36'
    }
    try:
        response = requests.get(url, params=params,headers=headers,timeout=3)
        selector = Selector(response.text)

        # 匹配所有车型卡片
        # 点评数量
        articles = selector.css('article.tw-grid')
        print(f"爬取第{i}页")
        count += len(articles)
        for article in articles:

            # 图片数量
            tupians = article.css("img.review-image")
            total_images += len(tupians)

            # 购买数量
            Vehicle_Model_div = article.css('div.tw-hidden')
            Vehicle_Model = Vehicle_Model_div.css('span.tw-flex-1::text').getall()
            Purchase_Quantity += int(len(Vehicle_Model))

            # 购买地点
            Places_div = article.css('div[class*="tw-flex-1"][class*="tw-relative"][class*="tw-py-12"]')
            Places = Places_div.css('p.tw-font-semibold::text').getall()
            if Places:
                if len(Places) < 1:
                    continue
                Place = Places[1].strip()
                if Place == "-":
                    continue
                Place_list.add(Place)

            # 评分
            score_blocks = article.css('div.tw-flex.tw-justify-around div.tw-text-center')

            # 存储当前点评的评分字典
            current_scores = {}

            for block in score_blocks:
                # 提取分数（内层的span.tw-relative）
                score_text = block.css('p.styles_score-item__2KcxU span.tw-relative '
                                       'span.tw-relative::text').get()

                # 提取名称（下面的p标签）
                name = block.css('p.tw-text-color-gray-700::text').get()
                if score_text and name:
                    score_text = score_text.strip()
                    name = name.strip()

                    # 用正则过滤，确保是数字
                    match = re.search(r'\d+\.?\d*', score_text)
                    if match:
                        current_scores[name] = float(match.group())

            # 2. 按名称存入对应列表，找不到的就跳过
            if '综合' in current_scores:
                Overall_score.append(current_scores['综合'])
            if '外观' in current_scores:
                Appearance_Score.append(current_scores['外观'])
            if '内饰' in current_scores:
                interior.append(current_scores['内饰'])
            if '配置' in current_scores:
                Configuration.append(current_scores['配置'])
            if '空间' in current_scores:
                space.append(current_scores['空间'])
            if '舒适性' in current_scores or '油耗' in current_scores:
                # 有的叫油耗，有的叫舒适性，根据你的题目调整
                if '舒适性' in current_scores:
                    Comfort.append(current_scores['舒适性'])
                elif '油耗' in current_scores:
                    Comfort.append(current_scores['油耗'])
            if '操控' in current_scores:
                Control.append(current_scores['操控'])

        # 3. 最后计算平均分（防止列表为空报错）
        if Overall_score:
            avg_Overall = round(sum(Overall_score) / len(Overall_score), 1)
        else:
            avg_Overall = 0.0
        time.sleep(0.5)

    except requests.exceptions.Timeout as e:
        print("请求超时", e)
    except requests.HTTPError as e:
        print("请求错误", e)
    except requests.exceptions.RequestException as e:
        print(e)

print(f'答案为：{count}-{total_images}-{Purchase_Quantity}-{len(Place_list)}-{avg_Overall}')


