#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 谢泽华
# @Date: 2026/5/30 21:02
# @Desc:

"""
使用 ddddocr 识别字体文件并创建映射表。
注意：个别字体或符号若不能被准确识别，可在此脚本中进行手动添加或修正。

"""
import json
import os
import ddddocr
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
import io


def process_font_with_ddddocr(font_path, output_mapping_path, unresolved_dir,suspicious_results=None):
    """
    使用 ddddocr 处理字体文件，生成确定字符的映射表和未确定字符的图片/记录

    :param font_path: 字体文件路径
    :param output_mapping_path: 确定字符映射表 JSON 文件保存路径
    :param unresolved_dir: 未确定字符图片及信息保存目录
    :param suspicious_results:列表或集合，包含被认为是“可疑错误”的识别文本。
    """

    if suspicious_results is None:
        suspicious_results = set()  # 默认不强制
    # 加载字体
    font = TTFont(font_path)
    cmap = font.getBestCmap()
    if not cmap:
        raise ValueError("字体文件中没有 cmap 表")

    # 初始化 ddddocr（beta 模型，可选）
    ocr = ddddocr.DdddOcr(beta=True)

    # 准备 PIL 字体（用于渲染）
    pil_font = ImageFont.truetype(font_path, size=120)

    # 创建未确定字符保存目录
    os.makedirs(unresolved_dir, exist_ok=True)

    # 结果存储
    determined_mapping = {}   # {hex_code: recognized_text}  置信度>=0.99
    unresolved_info = {}      # {hex_code: {"name": name, "recognized": text, "score": score}}

    total = len(cmap)
    count = 0

    for code, name in cmap.items():
        char = chr(code)
        # 渲染图片（300x300，字体大小120，居中偏上）
        img = Image.new('RGB', (300, 300), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        bbox = draw.textbbox((0, 0), char, font=pil_font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        x = (300 - w) / 2
        y = (300 - h) / 2 - 20
        draw.text((x, y), char, font=pil_font, fill=(0, 0, 0))

        # 可选：灰度 + 二值化（ddddocr 喜欢高对比图，但可能会丢失细节，可根据需要开启）
        # img = img.convert('L')
        # img = img.point(lambda x: 0 if x < 128 else 255, '1')
        # 注意：如果转为 '1' 模式，后续保存为 PNG 时需转换回 RGB 或保持灰度
        # 此处为了与 PaddleOCR 版本保持一致，不进行额外二值化

        # 将 PIL Image 转为字节流
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes = img_bytes.getvalue()

        # OCR 识别（带置信度）
        result = ocr.classification(img_bytes, probability=True)

        text = ""
        score = 0.0
        if result and isinstance(result, dict) and 'text' in result:
            text = result['text']
            score = result.get('confidence', 0.0)

        # 分类处理
        if text and score > 0.8 and text not in suspicious_results:
            determined_mapping[hex(code)] = text
        else:
            # 未确定字符
            unresolved_info[hex(code)] = {
                "name": name,
                "recognized": text if text else "",
                "score": score
            }
            # 保存图片（原始渲染图）
            img_filename = f"{hex(code)}.png"
            img.save(os.path.join(unresolved_dir, img_filename))

        count += 1
        if count % 100 == 0:
            print(f"已处理 {count}/{total} 个字符")

    # 保存确定字符的映射表
    with open(output_mapping_path, 'w', encoding='utf-8') as f:
        json.dump(determined_mapping, f, ensure_ascii=False, indent=2)

    # 保存未确定字符的信息
    unresolved_json_path = os.path.join(unresolved_dir, "unresolved.json")
    with open(unresolved_json_path, 'w', encoding='utf-8') as f:
        json.dump(unresolved_info, f, ensure_ascii=False, indent=2)

    # 打印统计信息
    print(f"处理完成。总字符数: {total}")
    print(f"确定字符数: {len(determined_mapping)}")
    print(f"未确定字符数: {len(unresolved_info)}")
    print(f"映射表保存至: {output_mapping_path}")
    print(f"未确定字符信息保存至: {unresolved_json_path}")
    print(f"未确定字符图片保存在: {unresolved_dir}")

    return determined_mapping, unresolved_info


if __name__ == '__main__':
    font_path = r"E:\crawler\爬虫基础\05-反爬\02-字体反爬\fonts\9ee8c2e770bb.woff2"
    output_mapping = "./mapping_ddddocr.json"
    unresolved_dir = "./unresolved_ddddocr"
    determined, unresolved = process_font_with_ddddocr(
        font_path,
        output_mapping,
        unresolved_dir,
        suspicious_results={"2", "一"}  # 将识别为"2"或"一"的都打入未确认
    )
