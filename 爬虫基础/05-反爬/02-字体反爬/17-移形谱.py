#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 谢泽华
# @Date: 2026/5/27 13:14
# @Desc: 静态字体反爬

"""
只有笨办法手动创建映射表
"""

import asyncio
import os
import requests
from parsel import Selector
from 爬虫基础.lib import to_float



base_url = "https://tc.xfei.tech/playground/static-font-map/ZW82XxIIaiC__7itSqA/zh/"

HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"
}

if not os.path.exists('./font'):
    os.makedirs('./font')


def get_html(url):
    for i in range(4):
        url = base_url
        params = {
            "offset" : 18 * i
        }
        response = requests.get(url, params=params,headers=HEADERS)
        html = response.text
        print(f"第{i+1}页")
        print(response.url)
        yield html


# 下载字体
def get_font(*url):
    if not url:
        url = "https://tc.xfei.tech/static/static-font-map/fonts/jiyun-cipher.woff2"
        HEADERS = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers = HEADERS)
        if os.path.exists("./font/jiyun-cipher.woff2"):
            print("字体文件已存在，跳过下载。")
            return True

        print("正在下载字体文件...")
        with open('./font/jiyun-cipher.woff2', 'wb') as f:
            f.write(response.content)
        print("字体下载成功！")
        return True


# 提取article
def get_article_node(html):
    selector = Selector(text=html)
    article_node = selector.xpath('//article[@class="movie-poster-card"]')
    for item in article_node:
        yield item



#  字符 <-> 码点 映射字典
codepoint_to_char = {
    0xE07F: '.',
    0xE09A: '2',
    0xE0B7: '4',
    0xE0D3: '7',
    0xE101: '0',
    0xE132: '1',
    0xE155: '5',
    0xE16E: '8',
    0xE18A: '6',
    0xE1A1: '9',
    0xE1C4: '3',
    0xE300: '·',
    0xE301: '一',
    0xE302: '万',
    0xE303: '三',
    0xE304: '上',
    0xE305: '不',
    0xE306: '专',
    0xE307: '世',
    0xE308: '东',
    0xE309: '丝',
    0xE30A: '丢',
    0xE30B: '个',
    0xE30C: '久',
    0xE30D: '之',
    0xE30E: '乡',
    0xE30F: '了',
    0xE310: '事',
    0xE311: '于',
    0xE312: '云',
    0xE313: '京',
    0xE314: '人',
    0xE315: '他',
    0xE316: '件',
    0xE317: '会',
    0xE318: '传',
    0xE319: '佛',
    0xE31A: '你',
    0xE31B: '佰',
    0xE31C: '保',
    0xE31D: '停',
    0xE31E: '先',
    0xE31F: '光',
    0xE320: '八',
    0xE321: '关',
    0xE322: '冠',
    0xE323: '剧',
    0xE324: '力',
    0xE325: '动',
    0xE326: '十',
    0xE327: '半',
    0xE328: '南',
    0xE329: '双',
    0xE32A: '叔',
    0xE32B: '变',
    0xE32C: '台',
    0xE32D: '吉',
    0xE32E: '同',
    0xE32F: '名',
    0xE330: '吒',
    0xE331: '味',
    0xE332: '和',
    0xE333: '哪',
    0xE334: '唐',
    0xE335: '喜',
    0xE336: '园',
    0xE337: '国',
    0xE338: '在',
    0xE339: '地',
    0xE33A: '坐',
    0xE33B: '堂',
    0xE33C: '声',
    0xE33D: '处',
    0xE33E: '大',
    0xE33F: '天',
    0xE340: '失',
    0xE341: '夺',
    0xE342: '女',
    0xE343: '好',
    0xE344: '如',
    0xE345: '妖',
    0xE346: '娜',
    0xE347: '孤',
    0xE348: '学',
    0xE349: '孩',
    0xE34A: '宇',
    0xE34B: '安',
    0xE34C: '宙',
    0xE34D: '家',
    0xE34E: '封',
    0xE34F: '小',
    0xE350: '少',
    0xE351: '山',
    0xE352: '崖',
    0xE353: '带',
    0xE354: '席',
    0xE355: '平',
    0xE356: '年',
    0xE357: '庄',
    0xE358: '弹',
    0xE359: '影',
    0xE35A: '得',
    0xE35B: '怒',
    0xE35C: '怪',
    0xE35D: '悬',
    0xE35E: '情',
    0xE35F: '意',
    0xE360: '愤',
    0xE361: '戏',
    0xE362: '成',
    0xE363: '我',
    0xE364: '战',
    0xE365: '才',
    0xE366: '扬',
    0xE367: '拆',
    0xE368: '拉',
    0xE369: '捕',
    0xE36A: '探',
    0xE36B: '斯',
    0xE36C: '无',
    0xE36D: '春',
    0xE36E: '是',
    0xE36F: '普',
    0xE370: '暴',
    0xE371: '最',
    0xE372: '朝',
    0xE373: '朱',
    0xE374: '杀',
    0xE375: '李',
    0xE376: '枝',
    0xE377: '椒',
    0xE378: '歌',
    0xE379: '气',
    0xE37A: '沼',
    0xE37B: '泽',
    0xE37C: '流',
    0xE37D: '浪',
    0xE37E: '海',
    0xE37F: '涉',
    0xE380: '深',
    0xE381: '热',
    0xE382: '焕',
    0xE383: '照',
    0xE384: '爱',
    0xE385: '狗',
    0xE386: '狮',
    0xE387: '球',
    0xE388: '生',
    0xE389: '界',
    0xE38A: '白',
    0xE38B: '的',
    0xE38C: '相',
    0xE38D: '祖',
    0xE38E: '神',
    0xE38F: '祥',
    0xE390: '秒',
    0xE391: '立',
    0xE392: '童',
    0xE393: '第',
    0xE394: '糕',
    0xE395: '糟',
    0xE396: '索',
    0xE397: '红',
    0xE398: '级',
    0xE399: '编',
    0xE39A: '缘',
    0xE39B: '罗',
    0xE39C: '而',
    0xE39D: '能',
    0xE39E: '英',
    0xE39F: '荔',
    0xE3A0: '药',
    0xE3A1: '蛇',
    0xE3A2: '血',
    0xE3A3: '行',
    0xE3A4: '裂',
    0xE3A5: '西',
    0xE3A6: '观',
    0xE3A7: '觉',
    0xE3A8: '记',
    0xE3A9: '话',
    0xE3AA: '诡',
    0xE3AB: '误',
    0xE3AC: '谁',
    0xE3AD: '象',
    0xE3AE: '走',
    0xE3AF: '起',
    0xE3B0: '超',
    0xE3B1: '辈',
    0xE3B2: '辑',
    0xE3B3: '过',
    0xE3B4: '还',
    0xE3B5: '追',
    0xE3B6: '道',
    0xE3B7: '那',
    0xE3B8: '部',
    0xE3B9: '都',
    0xE3BA: '里',
    0xE3BB: '金',
    0xE3BC: '钟',
    0xE3BD: '长',
    0xE3BE: '问',
    0xE3BF: '闹',
    0xE3C0: '队',
    0xE3C1: '阳',
    0xE3C2: '降',
    0xE3C3: '雄',
    0xE3C4: '雨',
    0xE3C5: '音',
    0xE3C6: '顿',
    0xE3C7: '风',
    0xE3C8: '飞',
    0xE3C9: '馆',
    0xE3CA: '驰',
    0xE3CB: '鬼',
    0xE3CC: '魔',
    0xE3CD: '麦',
    0xE3CE: '麻',
    0xE3CF: '黑',
    0xE3D0: '!',
    0xE3D1: ',',
    0xE3D2: ':',
    0xE3DA: '/',
}

# 解密函数
def decrypt_text(encrypted_str):
    if not encrypted_str:
        return ""
    decrypted = []
    for char in encrypted_str:
        # 获取字符的 Unicode 码点
        code = ord(char)
        # 查表替换
        decrypted.append(codepoint_to_char.get(code, char))
    return ''.join(decrypted)

# 提取数据
async def get_content(article_node):
    movie_list = []
    for item in article_node:
        name = item.xpath('.//span[@class="movie-name-label cipher-title-text"]/text()').get()
        score_math = item.xpath('.//span[@class="movie-rating-badge cipher-number"]/text()').get()

        day = item.xpath('.//p[@class="movie-back-subtitle"]/text()').get()
        box_office = item.xpath(
            './/div[contains(@class,"movie-back-stat-wide")]//span[@class="movie-back-value cipher-number"]/text()').get()
        hot = item.xpath(
            './/div[span[text()="热度"]]//span[@class="movie-back-value cipher-number"]/text()').get()
        want = item.xpath(
            './/div[span[text()="想看"]]//span[@class="movie-back-value cipher-number"]/text()').get()

        movie_list.append({
            "影片名称": decrypt_text(name).strip() if name else "",
            "评分": to_float(decrypt_text(score_math).split()[0]) if score_math else "",
            "上映天数": decrypt_text(day) if day else "",
            "实时票房(亿)": to_float(decrypt_text(box_office)) if box_office else "",
            "热度(万)": to_float(decrypt_text(hot)) if hot else "",
            "想看(万)": to_float(decrypt_text(want)) if want else ""
        })

    return  movie_list


async def main():
    moves_list = []
    # 1. 下载字体
    get_font()

    # 3. 获取页面并解析
    htmls = get_html(base_url)
    for html in htmls:
        article_nodes = get_article_node(html)
        movie_list = await get_content(article_nodes)
        for movie in movie_list:
            moves_list.append(movie)
            print(movie)


    print(len(moves_list))

    base = max(moves_list, key=lambda x: x["实时票房(亿)"])
    print(base)

asyncio.run(main())