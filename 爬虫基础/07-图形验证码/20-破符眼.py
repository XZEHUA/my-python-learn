#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 谢泽华
# @Date: 2026/6/11 19:43
# @Desc:

import asyncio
from urllib.parse import urljoin
from ddddocr import DdddOcr
from playwright.async_api import async_playwright
from 爬虫基础.lib import to_float

base_url = "https://tc.xfei.tech/playground/tender-ocr/ZW829lyNajHjf6yB3Tc/zh/"



async def fetch(url):
    ocr = DdddOcr(show_ad=False)
    async with async_playwright() as p:
        # 启动浏览器 (headless=False 可显示界面用于调试)
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)
        await page.wait_for_load_state("networkidle")

        # 提取数据, 如获取所有商品标题
        text_data = []
        page_num = 1
        while True:
            print(f"正在处理第 {page_num} 页")
            rows = await page.locator("tbody tr").all()
            for row in rows:
                cells = await row.locator("td").all_text_contents()
                clean_cells = [cells.strip() for cells in cells if cells.strip()]
                if len(clean_cells) == 7:
                    data = {
                        "公告ID": clean_cells[0],
                        "地区": clean_cells[1],
                        "发布时间": clean_cells[2],
                        "采购单位": clean_cells[3],
                        "项目名称": clean_cells[4],
                        "预算（万元）": to_float(clean_cells[5]),
                        "中标状态": clean_cells[6],
                    }
                    if data["预算（万元）"] >= 1000 and clean_cells[6] == '招标中':
                        text_data.append(data)

            next_btn = page.locator("text=下一页").first

            if await next_btn.is_disabled():
                print("没有下一页，结束")
                break

            for i in range(3):
                # 定位图片元素
                captcha_element = page.locator('#captcha-image')
                src = await captcha_element.get_attribute('src')
                img_url = urljoin(base_url, src)
                # 截图元素
                img_bytes = await captcha_element.screenshot(path="验证码截图.png")

                # 2. 异步调用 OCR（避免阻塞事件循环）
                result = await asyncio.to_thread(ocr.classification, img_bytes)
                print(f"图形验证码识别结果: {result}")

                # 3. 填写验证码输入框
                captcha_input = page.locator('#captcha-answer')  # 示例选择器
                await captcha_input.fill(result)
                await next_btn.click()
                await asyncio.sleep(1)
                # 3. 等待状态提示出现（最多等待 5 秒）
                status_text = await page.locator("#status-text").text_content()
                print(status_text)
                if '成功' in status_text:
                    page_num += 1
                    break
                else:
                    print(f"验证失败: {status_text}")
            else:
                # 三次验证都失败，可根据需求退出或报错
                print("验证码3次失败，退出")
                break

    await browser.close()
    return text_data

async def main():
    datas = await fetch(base_url)
    print(f"共{len(datas)}条数据")
    for data in datas:
        print(data)


if __name__ == "__main__":
    asyncio.run(main())
