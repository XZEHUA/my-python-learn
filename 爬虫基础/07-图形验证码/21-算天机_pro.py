#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 谢泽华
# @Date: 2026/6/17 16:11
# @Desc: 使用 PaddleOCR 识别验证码的异步爬虫

import asyncio
import base64
import cv2
import numpy as np
from urllib.parse import urljoin
import aiohttp
from paddleocr import PaddleOCR

# ==================== 初始化 OCR 引擎（只加载一次） ====================
# use_angle_cls=True 启用方向分类，lang='en' 使用英文模型（适合数字+字母验证码）
ocr_engine = PaddleOCR(use_angle_cls=True, lang='en')


# ==================== 图像预处理函数 ====================
def preprocess_image(img_bytes: bytes) -> bytes:
    """
    对验证码图片进行预处理，提高识别准确率。
    步骤：灰度化 → 高斯模糊 → 二值化（可调整阈值）
    """
    # 将字节流转为 OpenCV 图像
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("图像解码失败，可能图片数据损坏")

    # 灰度化
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 高斯模糊去噪
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)

    # 二值化（阈值 150 可根据实际验证码调整）
    _, binary = cv2.threshold(blurred, 150, 255, cv2.THRESH_BINARY)

    # 可选：形态学开运算去除孤立噪点
    # kernel = np.ones((1, 1), np.uint8)
    # binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

    # 将处理后的图像编码为 png 字节流
    _, encoded = cv2.imencode('.png', binary)
    return encoded.tobytes()


# ==================== 同步 OCR 识别函数 ====================
def sync_ocr(img_bytes: bytes) -> str:
    """
    同步执行 PaddleOCR 识别，返回识别的文本字符串。
    如果识别失败或置信度低，返回空字符串。
    """
    # 预处理图像
    processed = preprocess_image(img_bytes)

    # 保存临时文件（PaddleOCR 需要文件路径或图像数组）
    with open("temp_captcha.png", "wb") as f:
        f.write(processed)

    # 执行识别
    result = ocr_engine.ocr("temp_captcha.png", cls=True)

    # 解析结果
    if result and result[0]:
        # 提取所有文本框的文本，过滤低置信度（<0.5）
        texts = [line[1][0] for line in result[0] if line[1][1] > 0.5]
        recognized = "".join(texts)
        return recognized
    return ""


# ==================== 异步 OCR 包装 ====================
async def verify_captcha(img_bytes: bytes) -> str:
    """
    异步调用同步的 OCR 识别，避免阻塞事件循环。
    """
    loop = asyncio.get_running_loop()
    # 在默认线程池中运行同步函数
    return await loop.run_in_executor(None, sync_ocr, img_bytes)


# ==================== 网络请求函数 ====================
async def fetch_captcha(url: str, session: aiohttp.ClientSession, sem: asyncio.Semaphore,
                        page: int, headers: dict):
    """
    获取指定页的验证码图片 URL（通过 force_captcha=1 强制返回验证码）。
    返回 (image_url, items) 或 (None, None) 表示失败。
    如果直接成功（无验证码），则 items 不为 None。
    """
    params = {'page': page, 'force_captcha': '1'}
    async with sem:
        try:
            async with session.get(url, params=params, headers=headers) as resp:
                data = await resp.json()
                image_url = urljoin(url, data['data']['captcha']['image_url'])
                if data.get("success"):
                    # 可能直接返回数据（极少情况）
                    items = data.get('data', {}).get('items', [])
                    return image_url, items
                else:
                    # 返回验证码图片 URL
                    return image_url, None
        except Exception as e:
            print(f"获取验证码失败 (第{page}页): {e}")
            return None, None


async def fetch_data_with_answer(url: str, session: aiohttp.ClientSession,
                                  sem: asyncio.Semaphore, page: int,
                                  captcha_answer: str, headers: dict):
    """
    使用验证码答案请求数据。
    返回 (items, next_image_url) 或 (None, None) 表示验证码错误。
    """
    params = {'page': page, 'captcha_answer': captcha_answer}
    async with sem:
        try:
            async with session.get(url, params=params, headers=headers) as resp:
                data = await resp.json()
                if data.get("success"):
                    items = data.get('data', {}).get('items', [])
                    next_img_url = urljoin(url, data['data']['captcha']['image_url'])
                    print(next_img_url)
                    return items, next_img_url
                else:
                    # 验证码错误
                    return None, None
        except Exception as e:
            print(f"请求数据失败 (第{page}页): {e}")
            return None, None


async def download_image(image_url: str, session: aiohttp.ClientSession,
                         sem: asyncio.Semaphore) -> bytes:
    """
    下载验证码图片，返回原始字节。
    """
    if not image_url:
        return None
    async with sem:
        try:
            async with session.get(image_url) as resp:
                return await resp.read()
        except Exception as e:
            print(f"下载图片失败: {e}")
            return None


# ==================== 主程序 ====================
async def main():
    base_url = 'https://tc.xfei.tech/playground/trademark-opposition/ZW823fJKaj8Sf8NrQCI/zh/api/records'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36',
    }

    sem = asyncio.Semaphore(10)        # 控制并发
    filtered_list = []                 # 存储符合条件的数据
    page = 1
    max_pages = 90

    async with aiohttp.ClientSession() as session:
        # -------- 第一页：先获取验证码 --------
        print(f"正在处理第 {page} 页（获取验证码）...")
        img_url, items = await fetch_captcha(base_url, session, sem, page, headers)
        if items is not None:
            # 极小概率直接成功
            print("第一页直接成功，无需验证码。")
            filtereds = [item for item in items if item.get("risk_level") == 'high' and "审查中" in item.get("legal_status", "")]
            img_bytes = await download_image(img_url, session, sem)
            if not img_bytes:
                print("第一页验证码下载失败，退出。")
                return
            captcha_text = await verify_captcha(img_bytes)
            if not captcha_text:
                print("第一页验证码识别失败，退出。")
                return
            print(f"第 {page} 页验证码识别结果: {captcha_text}")
            filtered_list.extend(filtereds)
            page += 1
        else:
            # 下载并识别验证码
            img_bytes = await download_image(img_url, session, sem)
            if not img_bytes:
                print("第一页验证码下载失败，退出。")
                return
            captcha_text = await verify_captcha(img_bytes)
            if not captcha_text:
                print("第一页验证码识别失败，退出。")
                return
            print(f"第 {page} 页验证码识别结果: {captcha_text}")

            # 用答案请求第一页数据
            items, next_img_url = await fetch_data_with_answer(base_url, session, sem, page, captcha_text, headers)
            if items is None:
                print("第一页验证码错误，重试（这里可加入重试逻辑）")
                return
            filtereds = [item for item in items if item.get("risk_level") == 'high' and "审查中" in item.get("legal_status", "")]
            filtered_list.extend(filtereds)
            print(f"第 {page} 页收集 {len(filtereds)} 条，累计 {len(filtered_list)} 条")

            # 为下一页准备验证码
            current_captcha_url = next_img_url
            page += 1

        # -------- 循环处理第 2 至 90 页 --------
        while page <= max_pages:
            print(f"\n正在处理第 {page} 页...")

            # 下载当前页的验证码（由上一页返回）
            img_bytes = await download_image(current_captcha_url, session, sem)
            if not img_bytes:
                print(f"第 {page} 页验证码下载失败，尝试重新获取验证码...")
                # 重新获取该页验证码（fallback）
                img_url, _ = await fetch_captcha(base_url, session, sem, page, headers)
                if not img_url:
                    print("重新获取验证码失败，跳过此页。")
                    page += 1
                    continue
                img_bytes = await download_image(img_url, session, sem)
                if not img_bytes:
                    print("下载重试失败，跳过。")
                    page += 1
                    continue

            # 识别验证码
            captcha_text = await verify_captcha(img_bytes)
            if not captcha_text:
                print(f"第 {page} 页验证码识别失败，尝试重新获取验证码...")
                # 重新获取并识别（简单重试一次）
                img_url, _ = await fetch_captcha(base_url, session, sem, page, headers)
                if img_url:
                    img_bytes = await download_image(img_url, session, sem)
                    if img_bytes:
                        captcha_text = await verify_captcha(img_bytes)
                if not captcha_text:
                    print(f"第 {page} 页验证码识别再次失败，跳过此页。")
                    page += 1
                    continue
            print(f"第 {page} 页验证码识别结果: {captcha_text}")

            # 使用答案请求数据
            items, next_img_url = await fetch_data_with_answer(base_url, session, sem, page, captcha_text, headers)
            if items is None:
                print(f"第 {page} 页验证码错误，跳过此页（可增加重试）。")
                page += 1
                continue

            # 过滤并统计
            filtereds = [item for item in items if item.get("risk_level") == 'high' and "审查中" in item.get("legal_status", "")]
            filtered_list.extend(filtereds)
            print(f"第 {page} 页收集 {len(filtereds)} 条，累计 {len(filtered_list)} 条")

            # 更新当前验证码 URL 为下一页的
            current_captcha_url = next_img_url
            page += 1

    # 最终结果
    print(f"\n总计符合条件条目数: {len(filtered_list)}")


if __name__ == '__main__':
    asyncio.run(main())