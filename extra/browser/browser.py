import os
import re
import webbrowser
import json

# 加载替换规则表
with open("extra\\browser\\url_rewrite.json", "r", encoding="utf-8") as f:
    url_rewrites = json.load(f)

# 读取 tmp.txt 文件
with open('tmp.txt', 'r', encoding='utf-8') as f:
    action = f.read()

# 匹配网址：支持 http/https 和裸域名
url_pattern = re.compile(
    r"(https?://[^\s]+|(?:www\.)?[a-zA-Z0-9\-]+\.(com|cn|net|org|io|gov|edu|co)(/[^\s]*)?)"
)

#若未打开浏览器，则打开默认浏览器
if not webbrowser._browsers:
    webbrowser.register('default', None, webbrowser.BackgroundBrowser("C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"))
    webbrowser.get('default').open('')  # 打开默认浏览器

# 搜索网址
match = url_pattern.search(action)

if match:
    url = match.group(0)

    # 如果是裸域名，加 http://
    if not url.startswith("http"):
        url = "http://" + url

    # 检查是否需要重写
    for prefix, target in url_rewrites.items():
        if url.startswith(prefix):
            print(f"匹配到重写规则：{prefix} -> {target}")
            url = target
            break

    print(f"检测到链接：{url}，正在打开...")
    webbrowser.open(url)
else:
    print("未检测到可识别的网址链接。")
