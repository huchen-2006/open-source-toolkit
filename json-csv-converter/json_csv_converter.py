"""JSON / CSV 互转命令行工具

功能：在 JSON 与 CSV 之间双向转换，支持嵌套字段压平、字段并集、可选类型推断。
用法：
    python json_csv_converter.py json2csv data.json data.csv
    python json_csv_converter.py json2csv data.json data.csv --flatten
    python json_csv_converter.py csv2json data.csv data.json
    python json_csv_converter.py csv2json data.csv data.json --typed
    python json_csv_converter.py json2csv data.json -          # 输出到标准输出
环境：Python 3.8 及以上，仅使用标准库。
"""

import argparse
import csv
import json
import sys

MISSING = ""


def flatten(obj, prefix="", out=None):
    """把嵌套字典压平成 {"a.b.c": value} 形式。"""
    if out is None:
        out = {}
    if isinstance(obj, dict):
        if not obj and prefix:
            out[prefix] = ""
        for key, value in obj.items():
            new_prefix = "%s.%s" % (prefix, key) if prefix else str(key)
            flatten(value, new_prefix, out)
    elif isinstance(obj, list):
        if all(not isinstance(v, (dict, list)) for v in obj):
            out[prefix] = "; ".join("" if v is None else str(v) for v in obj)
        else:
            out[prefix] = json.dumps(obj, ensure_ascii=False)
    else:
        out[prefix] = "" if obj is None else obj
    return out


def pick_records(data):
    """从 JSON 顶层结构中取出记录列表。"""
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        list_values = [v for v in data.values() if isinstance(v, list)]
        if len(list_values) == 1:
            return list_values[0]
        return [data]
    return [data]


def json_to_csv(src, dst, use_flatten):
    # utf-8-sig 兼容 Windows 编辑器保存的带 BOM 文件
    with open(src, "r", encoding="utf-8-sig") as fh:
        data = json.load(fh)
    records = pick_records(data)

    rows = []
    for record in records:
        if isinstance(record, dict):
            rows.append(flatten(record) if use_flatten else
                        {k: ("" if v is None else
                             (json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v))
                         for k, v in record.items()})
        else:
            rows.append({"value": record})

    if not rows:
        print("JSON 中没有可转换的记录。")
        return 1

    headers = []
    seen = set()
    for row in rows:
        for key in row:
            if key not in seen:
                seen.add(key)
                headers.append(key)

    target = open(dst, "w", encoding="utf-8-sig", newline="") if dst != "-" else sys.stdout
    try:
        writer = csv.DictWriter(target, fieldnames=headers, restval=MISSING)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    finally:
        if target is not sys.stdout:
            target.close()
    print("已转换 %d 条记录，%d 个字段 -> %s" % (len(rows), len(headers), dst))
    return 0


def convert_value(text, typed):
    if not typed:
        return text
    lowered = text.strip().lower()
    if lowered in ("true", "false"):
        return lowered == "true"
    if lowered in ("null", "none", ""):
        return None
    try:
        if text.strip().lstrip("-").isdigit() and not text.startswith("0") or text.strip() in ("0",):
            return int(text)
        return float(text)
    except (TypeError, ValueError):
        return text


def expand_keys(row):
    """把 a.b.c 形式的表头还原为嵌套字典。"""
    result = {}
    for key, value in row.items():
        if key is None:
            continue
        parts = key.split(".")
        node = result
        for part in parts[:-1]:
            child = node.get(part)
            if not isinstance(child, dict):
                child = {}
                node[part] = child
            node = child
        node[parts[-1]] = value
    return result


def csv_to_json(src, dst, typed):
    handle = open(src, "r", encoding="utf-8-sig", newline="") if src != "-" else sys.stdin
    try:
        reader = csv.DictReader(handle)
        rows = []
        for row in reader:
            converted = {k: convert_value(v or "", typed) for k, v in row.items() if k is not None}
            rows.append(expand_keys(converted))
    finally:
        if handle is not sys.stdin:
            handle.close()

    text = json.dumps(rows, ensure_ascii=False, indent=2)
    if dst == "-":
        sys.stdout.write(text + "\n")
    else:
        with open(dst, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
        print("已转换 %d 条记录 -> %s" % (len(rows), dst))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description="JSON 与 CSV 双向转换工具")
    sub = parser.add_subparsers(dest="command", required=True)

    p1 = sub.add_parser("json2csv", help="JSON 转 CSV")
    p1.add_argument("source", help="输入 JSON 文件路径")
    p1.add_argument("target", help="输出 CSV 路径，- 表示标准输出")
    p1.add_argument("--flatten", action="store_true", help="将嵌套对象压平为点号字段")

    p2 = sub.add_parser("csv2json", help="CSV 转 JSON")
    p2.add_argument("source", help="输入 CSV 文件路径，- 表示标准输入")
    p2.add_argument("target", help="输出 JSON 路径，- 表示标准输出")
    p2.add_argument("--typed", action="store_true", help="尝试把数字/布尔/null 还原为对应类型")

    args = parser.parse_args(argv)

    try:
        if args.command == "json2csv":
            return json_to_csv(args.source, args.target, args.flatten)
        return csv_to_json(args.source, args.target, args.typed)
    except FileNotFoundError as exc:
        print("文件不存在: %s" % exc.filename)
        return 2
    except json.JSONDecodeError as exc:
        print("JSON 解析失败: 第 %d 行第 %d 列 - %s" % (exc.lineno, exc.colno, exc.msg))
        return 3


if __name__ == "__main__":
    sys.exit(main())
