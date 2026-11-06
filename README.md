# open-source-toolkit

一组开箱即用的日常小工具合集。全部零第三方依赖（网页工具除外，本身无需依赖），下载后即可运行，适合作为日常开发与办公的备用工具集。

## 工具列表

| 工具 | 目录 | 技术栈 | 一句话说明 |
| --- | --- | --- | --- |
| 剪贴板历史管理器 | [`clipboard-manager/`](clipboard-manager/) | Python + tkinter | 记录剪贴板文本历史，支持搜索、置顶、一键回填 |
| 重复文件查找器 | [`duplicate-finder/`](duplicate-finder/) | Python 标准库 | 按内容哈希找出完全重复的文件，只读不删 |
| JSON / CSV 互转工具 | [`json-csv-converter/`](json-csv-converter/) | Python 标准库 | 命令行双向转换，支持嵌套压平与类型推断 |
| 单文件番茄钟 | [`pomodoro-timer/`](pomodoro-timer/) | HTML + CSS + JS | 双击即用的番茄工作法计时器，localStorage 存统计 |
| 简易密码生成器 | [`password-generator/`](password-generator/) | Python 标准库 | 密码学安全随机密码、PIN、口令短语生成 |

## 目录结构

```
open-source-toolkit/
├── README.md
├── LICENSE
├── clipboard-manager/
│   ├── clipboard_manager.py
│   └── README.md
├── duplicate-finder/
│   ├── duplicate_finder.py
│   └── README.md
├── json-csv-converter/
│   ├── json_csv_converter.py
│   └── README.md
├── pomodoro-timer/
│   ├── index.html
│   └── README.md
└── password-generator/
    ├── password_generator.py
    └── README.md
```

## 环境要求

- Python 工具：Python 3.8 及以上，无需 `pip install` 任何东西
- 剪贴板管理器：需要 Windows 系统，且 Python 自带 `tkinter`
- 番茄钟：任意现代浏览器

## 快速开始

```bash
git clone https://github.com/huchen-2006/open-source-toolkit.git
cd open-source-toolkit
```

### 1. 剪贴板历史管理器（Windows）

```bash
python clipboard-manager/clipboard_manager.py
```

启动后会在后台记录复制的文本，双击历史条目即可重新复制。

### 2. 重复文件查找器

```bash
python duplicate-finder/duplicate_finder.py D:\Downloads
python duplicate-finder/duplicate_finder.py D:\Pictures --min-size 1048576 --json report.json
```

只输出报告，不会删除任何文件；确认后再自行清理。

### 3. JSON / CSV 互转

```bash
python json-csv-converter/json_csv_converter.py json2csv data.json data.csv --flatten
python json-csv-converter/json_csv_converter.py csv2json data.csv data.json --typed
```

### 4. 单文件番茄钟

直接双击 `pomodoro-timer/index.html`，或用浏览器打开。空格开始 / 暂停，`R` 重置。

### 5. 密码生成器

```bash
python password-generator/password_generator.py --length 20
python password-generator/password_generator.py --passphrase 4
```

## 设计原则

- **零依赖**：Python 工具只用标准库，不引入任何第三方包，避免环境问题
- **单文件**：每个 Python 工具都是单个脚本，方便单独复制使用；网页工具是单个 HTML 文件
- **默认安全**：查重工具只读不删，密码生成使用 `secrets` 密码学安全随机源
- **可离线**：全部工具断网可用，不发起任何网络请求，不上传任何数据

## 许可

本项目基于 [MIT License](LICENSE) 开源，版权归 huchen-2006 所有。
