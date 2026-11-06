# 重复文件查找器

按文件内容哈希查找完全重复的文件，纯 Python 标准库实现，只读扫描，不会删除或移动任何文件。

## 功能

- 三级比对策略：文件大小 → 头尾部分哈希 → 完整 SHA-256，兼顾速度与准确性
- 按「可回收空间」从大到小排序输出重复组
- 支持设置最小文件大小阈值，忽略小文件干扰
- 支持跳过隐藏文件与隐藏目录
- 支持导出 JSON 与 CSV 报告
- 自动统计重复文件数量与可回收磁盘空间

## 环境要求

- Python 3.8 及以上
- 仅使用标准库，无第三方依赖
- 支持 Windows / macOS / Linux

## 运行

```bash
# 扫描当前目录
python duplicate_finder.py

# 扫描指定目录
python duplicate_finder.py D:\Downloads

# 只关注大于 1 MB 的文件
python duplicate_finder.py D:\Downloads --min-size 1048576

# 跳过隐藏文件，并导出报告
python duplicate_finder.py D:\Pictures --no-hidden --json result.json --csv result.csv
```

## 参数说明

| 参数 | 说明 |
| --- | --- |
| `directory` | 要扫描的目录，默认当前目录 |
| `--min-size` | 小于该字节数的文件忽略，默认 1 |
| `--no-hidden` | 跳过以点开头的隐藏文件与目录 |
| `--json FILE` | 结果写入 JSON 文件 |
| `--csv FILE` | 结果写入 CSV 文件（Excel 可直接打开） |

## 输出示例

```
已扫描文件: 1523 个
重复组: 2 组，重复文件: 3 个，可回收空间: 48.6 MB
--------------------------------------------------------------------
[组 1] 24.3 MB  x2  节省 24.3 MB
    D:\Pictures\2024\trip.mp4
    D:\Pictures\备份\trip.mp4
```

## 说明

- 扫描结果只列出重复文件，删除请自行确认后操作，工具本身不具备删除能力。
- 无读取权限或路径过长的文件会被跳过，末尾会汇总提示跳过数量。
- 对于超大目录，建议先用 `--min-size` 提高阈值以减少哈希计算量。
