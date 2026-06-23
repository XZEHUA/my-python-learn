#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 谢泽华
# @Date: 2026/6/11 19:43
# @Desc:
import io
from ddddocr import DdddOcr
from PIL import Image

ocr = DdddOcr(show_ad=False)
def ocr_img(img_input):
    """
    识别验证码图片中的文字

    Args:
        img_input: 图片文件路径 (str) 或图片字节流 (bytes)

    Returns:
        识别出的字符串
    """
    # 1. 根据输入类型打开图片
    if isinstance(img_input, bytes):
        img = Image.open(io.BytesIO(img_input))
    else:
        img = Image.open(img_input)

    # 2. 图像预处理：灰度 → 二值化 → 转RGB（ddddocr要求）
    img = img.convert("L")  # 转灰度
    threshold = 220
    img = img.point(lambda x: 0 if x < threshold else 255, "1")  # 二值化
    img = img.convert("RGB")  # ddddocr 需要 RGB 模式

    # 3. OCR 识别
    result = ocr.classification(img)
    # print(result)
    return result