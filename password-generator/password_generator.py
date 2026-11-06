"""简易密码生成器

功能：基于标准库 secrets 生成高强度随机密码，支持长度、数量、字符集裁剪、口令短语与纯数字 PIN。
用法：
    python password_generator.py
    python password_generator.py --length 20 --count 5
    python password_generator.py --no-symbols --no-ambiguous
    python password_generator.py --passphrase 4
    python password_generator.py --pin 6
环境：Python 3.8 及以上，仅使用标准库。
"""

import argparse
import secrets
import string
import sys

LOWER = string.ascii_lowercase
UPPER = string.ascii_uppercase
DIGITS = string.digits
SYMBOLS = "!@#$%^&*()-_=+[]{};:,.?/"

AMBIGUOUS = "0Oo1lI|`'\"" + "\"" + "/\\"

# 用于生成口令短语的短词表，全部为常见英文单词，避免拼写歧义
WORDS = (
    "amber anchor apple arrow autumn badge bamboo beacon bridge butter cactus "
    "camera candle canyon carpet castle cedar cherry circle cloud cobalt comet "
    "copper coral cotton crystal daisy delta desert diamond dragon eagle ember "
    "engine falcon feather fern fiddle forest fossil galaxy garden ginger globe "
    "granite grape gravel harbor hazel honey indigo island ivory jade jungle "
    "kernel kettle ladder lantern lemon lilac linen lizard lotus lunar maple "
    "marble meadow melon meteor mirror mosaic nectar nickel nimble noble north "
    "oasis ocean olive onyx opal orbit orchid otter paddle pastel pebble pepper "
    "pewter pillow planet plum pocket pollen prairie prism puffin quartz quiver "
    "rabbit radar raven ribbon river robin rocket rubber saddle salmon sapphire "
    "shadow silver sketch slate socket spiral spruce squash stellar stone storm "
    "summit sunset syrup tablet tawny teapot thicket thunder timber topaz tower "
    "tulip tunnel turtle umber valley velvet violet walnut willow window winter "
    "yellow zephyr zigzag zipper"
).split()


def build_pool(no_symbols, no_ambiguous, letters_only):
    pools = []
    if letters_only:
        pools = [LOWER, UPPER]
    else:
        pools = [LOWER, UPPER, DIGITS, SYMBOLS]
        if no_symbols:
            pools = [LOWER, UPPER, DIGITS]
    if no_ambiguous:
        pools = ["".join(ch for ch in pool if ch not in AMBIGUOUS) for pool in pools]
    pools = [pool for pool in pools if pool]
    return pools


def generate_password(length, pools):
    if not pools:
        raise ValueError("字符集为空，无法生成密码")
    if length < len(pools):
        raise ValueError("长度至少需要 %d 位以覆盖所选字符类别" % len(pools))
    chars = [secrets.choice(pool) for pool in pools]
    combined = "".join(pools)
    while len(chars) < length:
        chars.append(secrets.choice(combined))
    # 洗牌，避免必选字符固定出现在前几位
    for index in range(len(chars) - 1, 0, -1):
        swap = secrets.randbelow(index + 1)
        chars[index], chars[swap] = chars[swap], chars[index]
    return "".join(chars)


def generate_pin(length):
    if length < 1:
        raise ValueError("PIN 长度必须大于 0")
    return "".join(secrets.choice(DIGITS) for _ in range(length))


def generate_passphrase(words, separator, capitalize):
    picked = [secrets.choice(WORDS) for _ in range(words)]
    if capitalize:
        picked = [word.capitalize() for word in picked]
    number = secrets.randbelow(90) + 10
    return separator.join(picked) + separator + str(number)


def strength_label(password):
    pool = 0
    if any(ch in LOWER for ch in password):
        pool += 26
    if any(ch in UPPER for ch in password):
        pool += 26
    if any(ch in DIGITS for ch in password):
        pool += 10
    if any(ch in SYMBOLS for ch in password):
        pool += len(SYMBOLS)
    if pool <= 0:
        return "未知"
    bits = len(password) * (pool.bit_length() - 1)
    if bits < 50:
        return "弱"
    if bits < 80:
        return "中"
    if bits < 120:
        return "强"
    return "很强"


def main(argv=None):
    parser = argparse.ArgumentParser(description="安全的随机密码生成器")
    parser.add_argument("-l", "--length", type=int, default=16, help="密码长度，默认 16")
    parser.add_argument("-c", "--count", type=int, default=1, help="生成条数，默认 1")
    parser.add_argument("--no-symbols", action="store_true", help="不包含特殊符号")
    parser.add_argument("--no-ambiguous", action="store_true", help="排除易混淆字符 0O o1lI 等")
    parser.add_argument("--letters-only", action="store_true", help="仅使用大小写字母")
    parser.add_argument("--pin", type=int, metavar="N", help="生成 N 位纯数字 PIN")
    parser.add_argument("--passphrase", type=int, metavar="N", help="生成 N 个单词组成的口令短语")
    parser.add_argument("--separator", default="-", help="口令短语分隔符，默认 -")
    parser.add_argument("--capitalize", action="store_true", help="口令短语首字母大写")
    args = parser.parse_args(argv)

    try:
        if args.pin:
            for _ in range(args.count):
                pin = generate_pin(args.pin)
                print(pin)
            return 0

        if args.passphrase:
            for _ in range(args.count):
                print(generate_passphrase(args.passphrase, args.separator, args.capitalize))
            return 0

        pools = build_pool(args.no_symbols, args.no_ambiguous, args.letters_only)
        for _ in range(args.count):
            password = generate_password(args.length, pools)
            print("%s    [强度: %s]" % (password, strength_label(password)))
        return 0
    except ValueError as exc:
        print("错误: %s" % exc)
        return 2


if __name__ == "__main__":
    sys.exit(main())
