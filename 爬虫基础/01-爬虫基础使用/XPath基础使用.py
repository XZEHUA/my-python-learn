#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 谢泽华
# @Date: 2026/5/8 23:37
# @Desc:

from parsel import Selector

html = '''
<div id="container" data-id="c1">
    <ul>
        <li class="comment" data-reply="yes" data-vip="yes">
            <a href="/user/1">Alice</a>
            <span class="rating">5</span>
            <p>剧情不错</p>
            <a>官方回复</a>
        </li>
        <li class="comment" data-reply="no">
            <a href="/user/2">Bob</a>
            <span class="rating">1</span>
            <p>差评</p>
        </li>
        <li class="comment">
            <a href="/user/3">Carol</a>
            <span class="rating">4</span>
            <p>演员一般</p>
        </li>
        <li class="ad">广告</li>
        <li class="comment">
            <a href="/user/4">David</a>
            <span class="rating">3</span>
            <p> 还 行 </p>
        </li>
    </ul>
</div>
'''

selector = Selector(text=html)
# res = selector.xpath('//ul/li/p/text()').getall()
# res = selector.xpath('//li/a/@href').getall()
# res = selector.xpath('//li/p[contains(text(),"差评")]/../a/@href').getall()
li_list = selector.xpath('//li[@class="comment"]')
for li in li_list:
    re = (li.xpath('./p/text()').get())
    res = li.xpath('./p').xpath('normalize-space(.)').get()
    print(re,res)