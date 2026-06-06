字体 OCR 字符映射提取工具 使用文档
====================

一、工具概述
------

本工具用于**自动提取字体文件中的字符映射关系**，结合 PaddleOCR 自动识别 + 人工复核修正，输出精准的字体 Unicode 码点与文字映射表，适用于字体反爬、字体解析等场景。

工具包含两个核心脚本：

1. `ocr_worker.py`：全自动字体字符 OCR 识别，拆分高置信度映射和待复核字符
2. `resolve_unresolved.py`：人工复核后，合并修正结果，更新映射表

* * *

二、运行环境
------

### 1. 脚本通用环境

* Python 版本：**3.6+**
* 依赖：仅使用 Python 标准库，**无额外第三方依赖**

### 2. ocr_worker.py 专用环境

* Python 版本：**必须使用 3.10**（Python 3.13 不兼容 PaddleOCR）
* 第三方依赖：PaddleOCR
* 推荐使用虚拟环境（conda/venv）隔离环境

* * *

三、脚本功能与参数说明
-----------

### 1. ocr_worker.py

#### 功能

遍历字体文件所有字符，渲染为图片后通过 PaddleOCR 识别：

* 置信度 ≥ 0.99：自动保存为**确定映射表**（JSON）
* 置信度 < 0.99 / 未识别：保存为**未确定记录**（图片 + JSON），用于人工复核

#### 参数说明

表格

| 参数名              | 必需  | 类型  | 说明                            |
| ---------------- | --- | --- | ----------------------------- |
| --font_path      | 是   | 字符串 | 字体文件路径（支持 .ttf/.woff2/.otf 等） |
| --mapping_path   | 是   | 字符串 | 确定字符映射表输出路径（JSON 格式）          |
| --unresolved_dir | 是   | 字符串 | 未确定字符保存目录（程序自动创建）             |

#### 输出文件

1. `{mapping_path}`：确定映射表，格式：

```json
{ 
    "0x4e00": "一",
     "0x4e8c": "丁"
 }
```

2. `{unresolved_dir}/unresolved.json`：未确定字符信息，格式：

```json
{
  "0x4e00": {
    "name": "uni4E00",
    "recognized": "",
    "score": 0.45
  }
}
```

3. `{unresolved_dir}/*.png`：未确定字符渲染图片（文件名 = Unicode 码点，如 `0x4e00.png`）

#### 使用示例

```bash
python ocr_worker.py --font_path ./fonts/example.woff2 --mapping_path ./output/determined_mapping.json --unresolved_dir ./output/unresolved
```

* * *

### 2. resolve_unresolved.py

#### 功能

读取未确定字符 JSON 和确定映射表，将**已手动填写正确文字**的条目合并到确定映射表，并从未确定列表中删除。

#### 参数说明

表格

| 参数名              | 必需  | 类型  | 说明                            |
| ---------------- | --- | --- | ----------------------------- |
| --unresolved_dir | 是   | 字符串 | 未确定字符目录（必须包含 unresolved.json） |
| --mapping_path   | 是   | 字符串 | 确定映射表路径（直接在原文件更新）             |

#### 使用示例

```bash
python resolve_unresolved.py --unresolved_dir ./output/unresolved --mapping_path ./output/determined_mapping.json
```

* * *

四、完整工作流程（必看）
------------

### 步骤 1：运行 OCR 初步识别

1. 切换到 Python 3.10 虚拟环境
2. 执行 `ocr_worker.py` 全自动识别

```bash
# 激活虚拟环境（二选一）
conda activate py310
# source venv310/bin/activate

# 运行脚本
python ocr_worker.py --font_path font.woff2 --mapping_path mapping.json --unresolved_dir ./unresolved
```

执行后得到两个输出：

* `mapping.json`：高置信度自动识别映射（可直接使用）
* `unresolved/`：待复核图片 + `unresolved.json`

* * *

### 步骤 2：人工复核未确定字符

1. 打开 `unresolved/unresolved.json`
2. 对照目录下的 PNG 图片，判断字形对应的正确文字
3. 将正确文字填入 `recognized` 字段

示例（修正前 → 修正后）：

```json
// 修正前
"0x4e00": {"name": "uni4E00", "recognized": "", "score": 0.45}

// 修正后
"0x4e00": {"name": "uni4E00", "recognized": "一", "score": 0.45}
```

* 无法辨认的字符：`recognized` 保持空字符串即可

* * *

### 步骤 3：合并修正后的字符

任意 Python 环境运行合并脚本，自动更新映射表：

```bash
python resolve_unresolved.py --unresolved_dir ./unresolved --mapping_path mapping.json
```

#### 输出示例

```textile
成功合并 42 个字符到 mapping.json
未确定字符剩余数量: 17
未解决条目仍保存在 ./unresolved/unresolved.json
```

* * *

### 步骤 4（可选）：重复复核 + 合并

对剩余未确定字符，重复**步骤 2、步骤 3**，直到 `unresolved.json` 清空为止。

* * *

五、注意事项
------

1. **字体处理耗时**：中文字体含数万个字符，处理可能耗时数小时，建议使用 GPU 加速（脚本默认启用 `device="gpu:0"`）

2. **Python 版本严格区分**：
   
   * `ocr_worker.py`：必须 Python 3.10
   * `resolve_unresolved.py`：Python 3.6+ 均可

3. **图片渲染优化**：识别效果不佳时，可调整脚本中 `size=120`、图片尺寸、文字坐标偏移

4. **JSON 编码**：所有文件使用 UTF-8 编码，中文无乱码

5. **JSON 格式规范**：手动编辑时请勿添加语法错误（推荐 VS Code 编辑）

6. **多字体处理**：为每个字体创建独立输出目录，避免文件覆盖

* * *

六、常见问题
------

### Q1：运行 ocr_worker.py 提示 No module named 'paddleocr'

**解决**：确认环境为 Python 3.10，执行安装命令：

```bash
pip install paddleocr
```

### Q2：合并后 unresolved.json 条目未减少

**解决**：检查 `recognized` 字段是否**非空、非空格**，空值会被脚本忽略。

### Q3：映射表出现重复 Unicode 码点

**解决**：脚本使用 `dict.update()` 合并，**人工修正结果会覆盖自动识别结果**（以人工为准）。

### Q4：字符图片偏斜，OCR 识别不准

**解决**：调整 `ocr_worker.py` 中渲染参数：字体大小、图片尺寸、文字绘制坐标。
