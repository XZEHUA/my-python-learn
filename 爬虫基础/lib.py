#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 谢泽华
# @Date: 2026/6/1 22:51
# @Desc:


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