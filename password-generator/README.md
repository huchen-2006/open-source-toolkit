# 简易密码生成器

基于 Python 标准库 `secrets` 的随机密码生成器，密码学安全随机源，命令行一行取用。

## 功能

- 默认生成 16 位密码，包含大小写字母、数字、特殊符号四类字符
- 保证所选字符类别每类至少出现一次，再随机洗牌打乱位置
- 可排除易混淆字符（`0` `O` `o` `1` `l` `I` `|` 等），避免抄错
- 可只使用字母，或去掉特殊符号，适配不同网站的密码规则
- 支持一次生成多条
- 支持生成纯数字 PIN 码
- 支持生成「单词 + 数字」形式的口令短语，好记又够长
- 附带粗略强度估算提示

## 环境要求

- Python 3.8 及以上
- 仅使用标准库 `secrets` / `string` / `argparse`

## 运行

```bash
# 默认：16 位、1 条
python password_generator.py

# 生成 20 位、5 条
python password_generator.py --length 20 --count 5

# 不含特殊符号，且排除易混淆字符
python password_generator.py --no-symbols --no-ambiguous

# 纯字母密码
python password_generator.py --letters-only --length 24

# 6 位数字 PIN
python password_generator.py --pin 6

# 4 个单词组成的口令短语
python password_generator.py --passphrase 4 --capitalize
```

## 参数说明

| 参数 | 说明 |
| --- | --- |
| `-l, --length` | 密码长度，默认 16 |
| `-c, --count` | 生成条数，默认 1 |
| `--no-symbols` | 不包含特殊符号 |
| `--no-ambiguous` | 排除易混淆字符 |
| `--letters-only` | 仅使用大小写字母 |
| `--pin N` | 生成 N 位纯数字 PIN |
| `--passphrase N` | 生成 N 个单词组成的口令短语 |
| `--separator` | 口令短语分隔符，默认 `-` |
| `--capitalize` | 口令短语单词首字母大写 |

## 输出示例

```
$ python password_generator.py --length 20
kR7#vq2mXz@Lp9nT4wBc    [强度: 很强]
```

## 说明

- 使用 `secrets` 模块而非 `random`，随机源来自操作系统熵池，适合生成真实凭据。
- 建议不同网站使用不同密码，并配合密码管理器保存。
- 本工具只在本地生成并打印结果，不联网、不保存、不上传任何内容。
