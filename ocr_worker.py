#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 谢泽华
# @Date: 2026/6/6 15:39
# @Desc:

import os
import sys
import json
import argparse
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
import numpy as np
import io
import warnings

# 1. 抑制 PaddlePaddle 的 GLOG 日志（最有效）
os.environ['GLOG_minloglevel'] = '2'      # 0=INFO,1=WARNING,2=ERROR,3=FATAL
os.environ['FLAGS_logtostderr'] = '0'     # 不输出到 stderr

# 2. 抑制 ccache 警告
os.environ['CCACHE_DISABLE'] = '1'

# 3. 抑制 PaddlePaddle 的 CUDNN 版本警告（如果确定版本匹配）
os.environ['FLAGS_cudnn_deterministic'] = '1'

# 4. 抑制 Python 的 UserWarning
warnings.filterwarnings('ignore')

# 5. 抑制 Paddle 内部的 C++ 日志（更彻底，但可能隐藏错误）
# 注意：这需要放在 import paddle 之前
os.environ['GLOG_minloglevel'] = '2'

from paddleocr import PaddleOCR

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def process_font(font_path, output_mapping_path, unresolved_dir):
    """
    处理字体文件，生成确定字符的映射表和未确定字符的图片/记录
    """
    # 加载字体
    font = TTFont(font_path)
    cmap = font.getBestCmap()

    # 初始化 OCR
    ocr = PaddleOCR(
        lang='ch',
        ocr_version="PP-OCRv5",
        text_det_limit_side_len=1316,
        text_det_thresh=0.2,
        text_det_box_thresh=0.5,
        text_det_unclip_ratio=1.8,
        text_rec_score_thresh=0.9,
        use_textline_orientation=True,
        device="gpu:0"
    )

    # 准备 PIL 字体（用于渲染）
    pil_font = ImageFont.truetype(font_path, size=120)

    # 创建未确定字符保存目录
    os.makedirs(unresolved_dir, exist_ok=True)

    # 结果存储
    determined_mapping = {}  # {code: recognized_text}  置信度>=0.99
    unresolved_info = {}  # {code: {"name": name, "recognized": text, "score": score}}

    total = len(cmap)
    count = 0

    for code, name in cmap.items():
        char = chr(code)
        # 渲染图片
        img = Image.new('RGB', (300, 300), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        bbox = draw.textbbox((0, 0), char, font=pil_font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        x = (300 - w) / 2
        y = (300 - h) / 2 - 20
        draw.text((x, y), char, font=pil_font, fill=(0, 0, 0))

        # OCR 识别
        result = ocr.predict(np.array(img))
        text = ""
        score = 0.0

        if result and len(result) > 0:
            first_item = result[0]
            if isinstance(first_item, (list, tuple)) and len(first_item) >= 2:
                second = first_item[1]
                if isinstance(second, (list, tuple)) and len(second) == 2:
                    text, score = second
                elif isinstance(second, str):
                    text = second
                    score = 1.0
            elif isinstance(first_item, dict):
                rec_texts = first_item.get('rec_texts', [])
                rec_scores = first_item.get('rec_scores', [])
                if rec_texts and len(rec_texts) > 0:
                    text = rec_texts[0]
                if rec_scores and len(rec_scores) > 0:
                    score = rec_scores[0]

        # 分类处理
        if text and score >= 0.99:
            determined_mapping[hex(code)] = text
        else:
            # 未确定字符
            unresolved_info[hex(code)] = {
                "name": name,
                "recognized": text if text else "",
                "score": score
            }
            # 保存图片
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

    # 打印统计信息（供主程序捕获）
    print(f"处理完成。总字符数: {total}")
    print(f"确定字符数: {len(determined_mapping)}")
    print(f"未确定字符数: {len(unresolved_info)}")
    print(f"映射表保存至: {output_mapping_path}")
    print(f"未确定字符信息保存至: {unresolved_json_path}")
    print(f"未确定字符图片保存在: {unresolved_dir}")


def main():

    parser = argparse.ArgumentParser(description="字体OCR处理脚本 (Python 3.10环境)")
    parser.add_argument("--font_path", required=True, help="字体文件路径")
    parser.add_argument("--mapping_path", required=True, help="确定字符映射表输出路径 (JSON)")
    parser.add_argument("--unresolved_dir", required=True, help="未确定字符保存目录")
    args = parser.parse_args()

    process_font(args.font_path, args.mapping_path, args.unresolved_dir)

if __name__ == "__main__":
    main()

