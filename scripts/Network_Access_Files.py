

import requests

res = requests.get("")

# 返回二进制文件
print(res.content)

