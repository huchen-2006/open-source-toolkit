"""重复文件查找器

功能：扫描指定目录，按"文件大小 + 内容哈希"三级比对找出内容完全相同的文件，输出重复组报告。
用法：
    python duplicate_finder.py <目录>
    python duplicate_finder.py D:\\Downloads --min-size 1024
    python duplicate_finder.py D:\\Pictures --json result.json --csv result.csv
    python duplicate_finder.py . --no-hidden
环境：Python 3.8 及以上，仅使用标准库。本工具只做只读扫描，不会删除或移动任何文件。
"""

import argparse
import hashlib
import json
import os
import sys
from collections import defaultdict

CHUNK = 1024 * 1024
PART_SIZE = 64 * 1024


def human(size):
    units = ["B", "KB", "MB", "GB", "TB"]
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return "%.1f %s" % (value, unit) if unit != "B" else "%d B" % size
        value /= 1024
    return "%d B" % size


def walk_files(root, min_size, skip_hidden):
    files = []
    errors = []
    for dirpath, dirnames, filenames in os.walk(root, onerror=errors.append):
        if skip_hidden:
            dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for name in filenames:
            if skip_hidden and name.startswith("."):
                continue
            path = os.path.join(dirpath, name)
            try:
                stat = os.stat(path)
            except OSError as exc:
                errors.append(exc)
                continue
            if not os.path.isfile(path) or stat.st_size < min_size:
                continue
            files.append((path, stat.st_size))
    return files, errors


def partial_digest(path, size):
    """头部 + 尾部 + 文件大小，快速排除大部分不同文件。"""
    digest = hashlib.sha256()
    digest.update(str(size).encode("ascii"))
    with open(path, "rb") as fh:
        digest.update(fh.read(PART_SIZE))
        if size > PART_SIZE * 2:
            fh.seek(-PART_SIZE, os.SEEK_END)
            digest.update(fh.read(PART_SIZE))
    return digest.hexdigest()


def full_digest(path):
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            block = fh.read(CHUNK)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


def find_duplicates(root, min_size=1, skip_hidden=True):
    files, errors = walk_files(root, min_size, skip_hidden)
    by_size = defaultdict(list)
    for path, size in files:
        by_size[size].append(path)

    groups = []
    for size, paths in by_size.items():
        if len(paths) < 2:
            continue
        by_partial = defaultdict(list)
        for path in paths:
            try:
                by_partial[partial_digest(path, size)].append(path)
            except OSError as exc:
                errors.append(exc)
        for candidates in by_partial.values():
            if len(candidates) < 2:
                continue
            by_full = defaultdict(list)
            for path in candidates:
                try:
                    by_full[full_digest(path)].append(path)
                except OSError as exc:
                    errors.append(exc)
            for hash_value, same in by_full.items():
                if len(same) > 1:
                    groups.append({
                        "hash": hash_value,
                        "size": size,
                        "count": len(same),
                        "paths": sorted(same),
                    })

    groups.sort(key=lambda g: (-g["size"] * (g["count"] - 1), -g["size"]))
    return groups, len(files), errors


def print_report(groups, scanned, errors):
    total_waste = 0
    dup_files = 0
    for group in groups:
        total_waste += group["size"] * (group["count"] - 1)
        dup_files += group["count"] - 1

    print("已扫描文件: %d 个" % scanned)
    print("重复组: %d 组，重复文件: %d 个，可回收空间: %s"
          % (len(groups), dup_files, human(total_waste)))
    print("-" * 68)
    for index, group in enumerate(groups, 1):
        print("[组 %d] %s  x%d  节省 %s"
              % (index, human(group["size"]), group["count"],
                 human(group["size"] * (group["count"] - 1))))
        for path in group["paths"]:
            print("    %s" % path)
        print("")
    if errors:
        print("跳过 %d 个无法访问的项目（权限或路径过长）" % len(errors))
    if not groups:
        print("未发现重复文件。")


def main(argv=None):
    parser = argparse.ArgumentParser(description="按内容哈希查找重复文件（只读，不删除）")
    parser.add_argument("directory", nargs="?", default=".", help="要扫描的目录，默认当前目录")
    parser.add_argument("--min-size", type=int, default=1, help="小于该字节数的文件忽略，默认 1")
    parser.add_argument("--no-hidden", action="store_true", help="跳过以点开头的隐藏文件与目录")
    parser.add_argument("--json", metavar="FILE", help="将结果写入 JSON 文件")
    parser.add_argument("--csv", metavar="FILE", help="将结果写入 CSV 文件")
    args = parser.parse_args(argv)

    root = os.path.abspath(args.directory)
    if not os.path.isdir(root):
        print("目录不存在: %s" % root)
        return 2

    groups, scanned, errors = find_duplicates(root, args.min_size, not args.no_hidden)

    if args.json:
        payload = {
            "root": root,
            "scanned_files": scanned,
            "duplicate_groups": groups,
        }
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)
        print("结果已写入 %s" % args.json)

    if args.csv:
        import csv
        with open(args.csv, "w", encoding="utf-8-sig", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow(["组号", "大小(字节)", "SHA256", "文件路径"])
            for index, group in enumerate(groups, 1):
                for path in group["paths"]:
                    writer.writerow([index, group["size"], group["hash"], path])
        print("结果已写入 %s" % args.csv)

    print_report(groups, scanned, errors)
    return 0


if __name__ == "__main__":
    sys.exit(main())
