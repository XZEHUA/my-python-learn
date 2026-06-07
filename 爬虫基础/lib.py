#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 谢泽华
# @Date: 2026/6/1 22:51
# @Desc:
import json

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# 清理文本
def clean_text(value):
    return (value or '-').strip()

# 安全转 float
def to_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return value


def to_number(text):
    try:
        return float(text.replace(",", ""))
    except (ValueError,AttributeError) as e:
        print("转换失败 {e}")
        return None


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

