import bz2

# 原始字符串
text = "query_index:17343c34-f19f-4561-89bd-09923d065b1a"

# 压缩字符串
compressed = bz2.compress(text.encode('utf-8'))
print("压缩后的数据:", compressed)

# 解压缩字符串
decompressed = bz2.decompress(compressed).decode('utf-8')
print("解压缩后的数据:", decompressed)
