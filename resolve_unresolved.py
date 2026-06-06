#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 谢泽华
# @Date: 2026/6/6 19:15
# @Desc:

"""
resolve_unresolved.py

使用方法：
    python resolve_unresolved.py --unresolved_dir ./output/unresolved --mapping_path ./output/determined_mapping.json

功能：
    1. 读取 unresolved_dir 中的 unresolved.json。
    2. 遍历每个未确定字符条目，如果 "recognized" 字段不为空字符串，则将其作为正确识别结果。
    3. 将这些条目的码点及 recognized 值添加到 determined_mapping.json 中（已有条目会被覆盖或保留最新）。
    4. 从 unresolved.json 中删除已解决的条目。
    5. 保存更新后的 determined_mapping.json 和 unresolved.json。
"""

import json
import os
import argparse


def merge_resolved(unresolved_dir, mapping_path):
    unresolved_json = os.path.join(unresolved_dir, "unresolved.json")

    if not os.path.exists(unresolved_json):
        print(f"错误：找不到 {unresolved_json}")
        return False

    # 加载 unresolved.json
    with open(unresolved_json, 'r', encoding='utf-8') as f:
        unresolved = json.load(f)

    # 加载现有的确定映射表（如果存在）
    if os.path.exists(mapping_path):
        with open(mapping_path, 'r', encoding='utf-8') as f:
            determined = json.load(f)
    else:
        determined = {}

    # 找出已确认的条目（recognized 非空且不是空字符串）
    resolved_items = {}
    remaining = {}
    for code, info in unresolved.items():
        recognized = info.get("recognized", "").strip()
        if recognized:
            resolved_items[code] = recognized
        else:
            remaining[code] = info

    if not resolved_items:
        print("没有发现已确认的字符（recognized 字段为空）。")
        return False

    # 合并到确定映射表
    determined.update(resolved_items)

    # 保存更新后的确定映射表
    with open(mapping_path, 'w', encoding='utf-8') as f:
        json.dump(determined, f, ensure_ascii=False, indent=2)

    # 保存更新后的 unresolved.json（移除已解决的条目）
    with open(unresolved_json, 'w', encoding='utf-8') as f:
        json.dump(remaining, f, ensure_ascii=False, indent=2)

    print(f"成功合并 {len(resolved_items)} 个字符到 {mapping_path}")
    print(f"未确定字符剩余数量: {len(remaining)}")
    if len(remaining) > 0:
        print(f"未解决条目仍保存在 {unresolved_json}")
    else:
        print("所有未确定字符已处理完毕！")

    return True


def main():
    parser = argparse.ArgumentParser(description="将未确定字符中手动确认的部分合并到确定字符映射表")
    parser.add_argument("--unresolved_dir", required=True, help="未确定字符保存目录（包含 unresolved.json）")
    parser.add_argument("--mapping_path", required=True, help="确定字符映射表文件路径 (JSON)")
    args = parser.parse_args()

    merge_resolved(args.unresolved_dir, args.mapping_path)


if __name__ == "__main__":
    main()