#-*-coding:utf-8-*-

# 分段加密
CHUNK_SIZE = 30

# RSA加密
def enctypt(e, m, c):
    return pow(c, e, m)

# 加密一段
def enctypt_chunk(e, m, chunk):
    chunk = map(ord, chunk)

    # 补成偶数长度
    if not len(chunk) % 2 == 0:
        chunk.append(0)

    nums = [ chunk[i] + (chunk[i+1] << 8) for i in range(0, len(chunk), 2) ]

    c = sum([n << i*16 for i, n in enumerate(nums)])

    encypted = enctypt(e, m, c)

    # 转成16进制并且去掉开头的0x
    return hex(encypted)[2:]

# 加密字符串，如果比较长，则分段加密
def encrypt_string(e, m, s):
    e, m = int(e, 16), int(m, 16)

    chunks = [ s[:CHUNK_SIZE], s[CHUNK_SIZE:] ] if len(s) > CHUNK_SIZE else [s]

    result = [enctypt_chunk(e, m, chunk) for chunk in chunks]
    return ' '.join(result)[:-1] # 去掉最后的'L'

