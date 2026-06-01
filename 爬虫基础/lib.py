#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 谢泽华
# @Date: 2026/6/1 22:51
# @Desc:


# 清理文本
def clean_text(value):
    return (value or '-').strip()

# 安全转 float
def to_float(value, default=0.0):
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def to_number(text):
    try:
        return float(text.replace(",", ""))
    except (ValueError,AttributeError) as e:
        print("转换失败 {e}")
        return None