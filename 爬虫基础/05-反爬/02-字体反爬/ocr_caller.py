#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 谢泽华
# @Date: 2026/6/6 20:03
# @Desc: 封装调用 Python 3.10 环境中的 ocr_worker.py

import subprocess
import json
from pathlib import Path
import os

# Python 3.10 环境配置
PY310_PYTHON = r"D:\Miniconda3\envs\paddle_gpu\python.exe"
# ocr_worker.py 的路径
WORKER_SCRIPT = os.path.join(os.path.dirname(__file__), r"E:\crawler\ocr_worker.py")

def build_mapping_with_paddleocr(font_path, mapping_path, unresolved_dir):
    """调用 Python 3.10 环境中的 ocr_worker.py 生成映射表"""
    # 确保必要的脚本存在
    if not os.path.exists(PY310_PYTHON):
        raise FileNotFoundError(f"Python 3.10 解释器不存在: {PY310_PYTHON}")
    if not os.path.exists(WORKER_SCRIPT):
        raise FileNotFoundError(f"ocr_worker.py 脚本不存在: {WORKER_SCRIPT}")

    cmd = [
        PY310_PYTHON,
        WORKER_SCRIPT,
        "--font_path", font_path,
        "--mapping_path", mapping_path,
        "--unresolved_dir", unresolved_dir
    ]
    print(f"正在运行 OCR 处理: {' '.join(cmd)}")
    try:
        # 根据字体大小，超时时间可能需要调大（例如 600 秒）
        result = subprocess.run(cmd, check=True, timeout=600, )
        print("OCR 输出:", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"OCR 进程错误 (code {e.returncode}): {e.stderr}")
        return False
    except subprocess.TimeoutExpired:
        print("OCR 处理超时")
        return False
    except Exception as e:
        print(f"调用 OCR 时发生异常: {e}")
        return False



def find_worker_script():
    """从多个可能位置查找 ocr_worker.py"""
    # 1. 与当前脚本同目录
    p1 = Path(__file__).parent / "ocr_worker.py"
    if p1.exists():
        return p1
    # 2. 当前工作目录
    p2 = Path.cwd() / "ocr_worker.py"
    if p2.exists():
        return p2
    # 3. 向上递归查找（最多3级），直到找到根目录标记
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