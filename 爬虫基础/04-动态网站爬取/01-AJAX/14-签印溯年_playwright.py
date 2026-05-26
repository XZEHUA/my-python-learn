#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 谢泽华
# @Date: 2026/5/21 12:22
# @Desc:

from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("https://tc.xfei.tech/playground/movie-list-ajax-token/ZW82KVoNahI_f4Qk11Y/zh")
    page.wait_for_selector(".movie-item")
    # page.screenshot(path="./movie.png")
    print(page.title())
    page.close()
    browser.close()