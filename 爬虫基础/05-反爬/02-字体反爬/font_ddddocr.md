字体映射生成工具 (ddddocr)
==================

简介
--

本工具用于处理自定义字体文件（如 TTF、WOFF2 等），通过 **ddddocr** 对字体中每个字形进行渲染和识别，自动生成字符代码（unicode）与识别文本之间的映射表。对于识别置信度较低的字符，工具会保存其渲染图片及识别信息，便于人工复核。

适用于**字体反爬**场景中映射表的快速生成。
主要功能
----

* 加载字体文件的 `cmap` 表，获取所有字符的 unicode 编码和字形名称

* 使用 PIL 将每个字符渲染为高对比图片

* 调用 ddddocr（beta 模型）进行识别，并获取置信度

* 根据置信度阈值（默认 > 0.8）自动区分：
  
  * **确定字符**：保存为 JSON 映射表
  
  * **未确定字符**：保存原始渲染图片及识别信息（JSON），供人工核对

* 支持 `.ttf`, `.woff`, `.woff2` 等格式（需 `fontTools` 加载）

依赖安装
----

推荐使用 Python 3.7+，运行以下命令安装所需库：

```bash
pip install pillow fontTools ddddocr
```




## 使用方法

1. 准备字体文件（如 `custom.woff2`）

2. 修改脚本 `__main__` 中的参数，或直接调用 `process_font_with_ddddocr` 函数

### 命令行直接运行

```python
python font_mapping.py
```




### 函数调用示例

```python
from font_ddddocr import process_font_with_ddddocr

font_path = "path/to/your/font.woff2"
output_mapping = "./mapping_ddddocr.json"
unresolved_dir = "./unresolved_ddddocr"
determined, unresolved = process_font_with_ddddocr( 
    font_path=font_path,
    output_mapping_path=output_mapping, 
    unresolved_dir=unresolved_dir
)
```


参数说明

| 参数                    | 类型    | 说明                                   |
| --------------------- | ----- | ------------------------------------ |
| `font_path`           | `str` | 字体文件路径（支持 `.ttf`, `.woff`, `.woff2`） |
| `output_mapping_path` | `str` | 确定字符映射表保存路径（JSON 格式）                 |
| `unresolved_dir`      | `str` | 未确定字符图片及信息保存目录（自动创建）                 |

输出结果
----

### 1. 确定字符映射表 (`mapping_ddddocr.json`)

```json
{ 
    "0x4e00": "中",
     "0x4e01": "国", 
    ...
}
```

* 键：字符 unicode 的十六进制表示

* 值：ddddocr 识别出的文本

### 2. 未确定字符目录 (`unresolved_ddddocr/`)

* `unresolved.json`：未确定字符的详细信息
  
  ```json
  { 
  "0x1234": {
      "name": "uni1234",
      "recognized": "？",
      "score": 0.65
      }, 
  ...
  }
  ```
  
  

* 每个未确定字符会生成一张 PNG 图片，文件名为 `{hex_code}.png`，例如 `0x1234.png`，便于人工核对。

配置调整
----

* **置信度阈值**：代码中默认使用 `score > 0.8` 作为确定标准，可根据实际效果修改第 79 行。

* **图片尺寸**：渲染图片大小为 300×300，字体大小 120 像素。若识别效果不佳，可调整 `Image.new` 和 `ImageFont.truetype` 参数。

* **图像预处理**：代码中保留了灰度/二值化的注释，若需要可取消注释以提高识别准确率（可能丢失部分细节）。

注意事项
----

1. **字体支持**：必须包含 `cmap` 表，否则无法获取字符映射。部分字体可能包含大量字符，处理时间较长（约每秒 20~50 个字符）。

2. **ddddocr 模型**：`beta=True` 会启用新版模型，识别精度更高，但速度稍慢。可根据需求改为 `beta=False`。

3. **内存使用**：对于超大字体（如 CJK 全字集），建议分批处理或使用更高配置机器。

4. **人工复核**：未确定字符通常是生僻字、特殊符号或渲染变形导致，建议通过查看图片手动确认映射关系。

常见问题与处理建议（根据实际测试反馈）
-------------------

### 1. 识别结果错误：例如“？”被识别为“2”

**现象**：  字体中的问号“？”字形与数字“2”相似，ddddocr 错误输出 `"2"`。

**解决方案**：  在生成的映射表中增加**替换规则**，将识别为 `"2"` 的条目修正为 `"？"`

```python
import json

with open("mapping_ddddocr.json", "r", encoding="utf-8") as f:
    mapping = json.load(f)

corrections = {
    "2": "？",    # 将识别为 "2" 的改为问号
    # 可添加其他常见错误： "0" -> "O", "1" -> "l" 等
}

new_mapping = {}
for code, wrong_char in mapping.items():
    new_mapping[code] = corrections.get(wrong_char, wrong_char)

with open("mapping_corrected.json", "w", encoding="utf-8") as f:
    json.dump(new_mapping, f, ensure_ascii=False, indent=2)
```

### 2. 同一个汉字出现多次，实为另一个字被误识别（例如“二”被识别成“一”，导致有两个“一”）

**现象**：  映射表中包含两个不同码位都对应 `"一"`，其中一个是真正的“一”，另一个是“二”被误识别为“一”。
**解决方案**： 修改分类规则，识别出“2”或“一”就放入未确认目录


