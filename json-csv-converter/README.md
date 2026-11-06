# JSON / CSV 互转命令行工具

一个零依赖的命令行转换工具，在 JSON 与 CSV 之间双向转换，适合处理接口导出的 JSON 数据与 Excel 报表数据。

## 功能

- `json2csv`：JSON 转 CSV，自动取所有记录的字段并集作为表头，缺失字段留空
- `csv2json`：CSV 转 JSON，支持把表头还原为嵌套结构
- `--flatten`：把嵌套对象压平为 `a.b.c` 形式的点号字段，适合宽表导出
- `--typed`：CSV 转 JSON 时推断数字、布尔值、null 类型，避免全部变成字符串
- 支持 `-` 作为输入 / 输出，配合管道与其他命令串联
- 输出 CSV 使用 UTF-8 BOM 编码，Excel 打开中文不乱码

## 环境要求

- Python 3.8 及以上
- 仅使用标准库 `argparse` / `csv` / `json`

## 运行

```bash
# JSON 转 CSV
python json_csv_converter.py json2csv data.json data.csv

# 嵌套 JSON 压平后转 CSV
python json_csv_converter.py json2csv data.json data.csv --flatten

# CSV 转 JSON，并自动推断类型
python json_csv_converter.py csv2json data.csv data.json --typed

# 输出到标准输出，便于管道处理
python json_csv_converter.py json2csv data.json -
```

## 输入格式约定

`json2csv` 支持以下三种 JSON 结构：

```jsonc
// 1. 记录数组（推荐）
[{"name": "张三", "age": 20}, {"name": "李四", "age": 21}]

// 2. 单条记录对象
{"name": "张三", "age": 20}

// 3. 仅含一个数组字段的包装对象
{"data": [{"name": "张三", "age": 20}]}
```

对嵌套字段的处理：

- 默认：嵌套对象与数组会被序列化为 JSON 字符串放进单元格
- 加 `--flatten`：嵌套对象展开为 `address.city` 这样的独立列

`csv2json` 识别 `a.b` 形式的表头并自动还原为嵌套对象，`--typed` 时 `123`、`3.14`、`true`、`null` 会转换为对应类型。

## 退出码

| 退出码 | 含义 |
| --- | --- |
| 0 | 转换成功 |
| 1 | JSON 中没有可转换的记录 |
| 2 | 文件不存在 |
| 3 | JSON 语法错误 |
