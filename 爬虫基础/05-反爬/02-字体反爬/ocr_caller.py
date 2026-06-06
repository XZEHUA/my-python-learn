#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 谢泽华
# @Date: 2026/6/6 20:03
# @Desc: 封装调用 Python 3.10 环境中的 ocr_worker.py

import subprocess
import json
import os
from pathlib import Path

def find_worker_script():
    """从多个可能位置查找 ocr_worker.py"""
    # 1. 与当前脚本同目录
    p1 = Path(__file__).parent / "ocr_worker.py"
    if p1.exists():
        return p1
    # 2. 当前工作目录（可能是项目根目录）
    p2 = Path.cwd() / "ocr_worker.py"
    if p2.exists():
        return p2
    # 3. 向上递归查找（最多3级），直到找到根目录标记（如 .git 或 requirements.txt）
    for parent in Path(__file__).parents:
        p3 = parent / "ocr_worker.py"
        if p3.exists():
            return p3
        if (parent / ".git").exists() or (parent / "requirements.txt").exists():
            # 找到项目根目录，停止向上
            break
    return None

def run_ocr_on_font(
        font_path: str,
        mapping_output_path: str,
        unresolved_output_dir: str,
        python310_interpreter: str
) -> dict:
    """
    调用 Python 3.10 环境中的 ocr_worker.py 处理字体文件

    参数：
        font_path: 字体文件路径
        mapping_output_path: 生成的确定映射表 JSON 文件路径
        unresolved_output_dir: 未确定字符保存目录
        python310_interpreter: Python 3.10 解释器的绝对路径

    返回：
        {
            "success": bool,
            "message": str,
            "mapping": dict
        }
    """
    worker_script = find_worker_script()
    if worker_script is None:
        return {
            "success": False,
            "message": "找不到 ocr_worker.py，请确保它在项目根目录或与调用脚本同目录",
            "mapping": {}
        }

    cmd = [
        python310_interpreter,
        str(worker_script),
        "--font_path", font_path,
        "--mapping_path", mapping_output_path,
        "--unresolved_dir", unresolved_output_dir
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8',
            timeout=600  # 10分钟超时，可根据字体大小调整
        )
        # 子进程成功执行，读取生成的映射表
        with open(mapping_output_path, 'r', encoding='utf-8') as f:
            mapping = json.load(f)

        return {
            "success": True,
            "message": result.stdout,
            "mapping": mapping
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "message": "OCR 处理超时（超过600秒）",
            "mapping": {}
        }
    except subprocess.CalledProcessError as e:
        return {
            "success": False,
            "message": f"子进程错误 (code {e.returncode}):\n{e.stderr}",
            "mapping": {}
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"其他错误: {str(e)}",
            "mapping": {}
        }