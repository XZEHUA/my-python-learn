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
import ddddocr
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
import io


def build_mapping_with_ddddocr(font_path,storage_path=None):
    """
     读取字体文件，通过 OCR 生成加密字符到真实字符的映射表，并保存为 JSON 文件。

    :param font_path: 字体文件路径 (如 .woff, .ttf)
    :param storage_path: 映射表 JSON 文件的保存目录路径（可选）
    :return: 生成的映射字典
    """
    # 打开 WOFF2 文件
    font = TTFont(font_path)

    # 保存为 TTF 格式
    # font_filename =font_path.replace(".woff2", ".ttf")
    # font.save(font_filename)

    cmap = font.getBestCmap()
    if not cmap:
        raise ValueError("字体文件中没有 cmap 表")

    draw_font = ImageFont.truetype(font_path, size=90)
    ocr = ddddocr.DdddOcr(beta=True)
    mapping = {}

    for codepoint, glyph_name in cmap.items():
        # 跳过未定义字符
        if glyph_name == '.notdef':
            continue

        char = chr(codepoint)
        # 创建画布
        img = Image.new('RGB', (150, 150), 'white')
        draw = ImageDraw.Draw(img)
        draw.text((12, 12), char, font=draw_font, fill='black',)

        # 转为灰度并二值化（ddddocr 也喜欢高对比图）
        img = img.convert('L')
        img = img.point(lambda x: 0 if x < 128 else 255, '1')

        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes = img_bytes.getvalue()

        # 调用 OCR 进行识别
        recognized = ocr.classification(img_bytes)
        if recognized:
            hex_key = f"0x{codepoint:04X}"
            mapping[hex_key] = recognized
        else:
            print(f"\33[33m警告: codepoint {hex(codepoint)} 未识别出任何字符!\033[0m")


    # 确定最终的文件保存路径
    file_path = storage_path  if storage_path else "mapping.json"
    with open(file_path, 'w',encoding="utf-8") as f:
        # ensure_ascii = False 保留中文或特殊符号的原貌
        json.dump(mapping, f,ensure_ascii=False,indent=2)

    return mapping

def merge_manual_mapping(mapping_path,known_mapping):
    """
      将手动定义的映射表合并到指定的 JSON 映射文件中。
      定义已知的码点->真实字符
    known_mapping = {
        0xE07F: '.',
        0xE300: '·',
        0xE3d0: '!',
        0xE132: '1',
    }
      """

    if not known_mapping:
        return mapping_path
    # 1. 【读取】从文件中加载现有的映射表
    with open(mapping_path, 'r', encoding="utf-8") as f:
        mapping = json.load(f)

    # 2. 【修改】在内存中遍历并更新字典
    for codepoint, real_char in known_mapping.items():
        hex_key = f"0x{codepoint:04X}"
        mapping[hex_key] = real_char  # 如果已存在则覆盖，不存在则新增

    # 3. 【写入】将最终完整的字典一次性写回文件
    with open(mapping_path, 'w', encoding="utf-8") as f:
        json.dump(mapping, f,ensure_ascii=False,indent=2)
        print(f"已成功添加/修改 {len(known_mapping)} 条映射到 {mapping_path}")
    return mapping_path

# 解密函数
def decrypt_text(mapping_path, encrypted_str):
    """
         根据映射表文件对加密字符串进行解密还原。

    :param mapping_path: 映射表 JSON 文件的路径
    :param encrypted_str: 包含自定义字体的加密字符串
    :return: 解密后的正常文本
    """

    # 兼容列表和字符串类型：如果传入的是列表，先将其拼接成一个完整的字符串
    if isinstance(encrypted_str, list):
        encrypted_str = ''.join(encrypted_str)

    if not encrypted_str:
        return ""
    # 逐个字符替换（因为映射表可能只覆盖部分字符）
    result = []
    with open(mapping_path, 'r', encoding="utf-8") as f:
        mapping = json.load(f)
        # 逐个字符替换

        for ch in encrypted_str:
            hex_key = f"0x{ord(ch):04x}"
            real_char = mapping.get(hex_key, ch)
            result.append(real_char)
        return ''.join(result)


if __name__ == '__main__':
    font_file_path = './font/jiyun-cipher.woff2'
    build_mapping_with_ddddocr(font_file_path,"./font/mapping.json")
    merge_manual_mapping("./font/mapping.json",  known_mapping = {
        0xE07F: '.',
        0xE300: '·',
        0xE3d0: '!',
        0xE132: '1',
    })

    raw_html = '<div>影片名称: <span class="stonefont">\ue328\ue313\ue383相馆;</span></div>'
    cleaned = decrypt_text("./font/mapping.json",raw_html)

    print("清洗后:", cleaned)
