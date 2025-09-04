import os
import json
from google import genai
from google.genai import types

# 打开config.json文件
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
    API_KEY = config.get('Gemini_key', '')
    HISTORY_LIMIT = config.get('history_length', 10)

# 初始化 Gemini 客户端
client = genai.Client(
    api_key=API_KEY,
)

def extract_json(raw_str: str) -> str:
    """
    从 raw_str 中提取第一个完整的 JSON 对象字符串（以 { 开始，到匹配的 } 结束）。
    如果未找到完整对象，则返回空串。
    """
    start = raw_str.find('{')
    if start == -1:
        return ""
    
    brace_level = 0
    for idx, ch in enumerate(raw_str[start:], start=start):
        if ch == '{':
            brace_level += 1
        elif ch == '}':
            brace_level -= 1
            if brace_level == 0:
                # 找到与第一个 { 匹配的 }，返回子串
                return raw_str[start:idx+1]
    
    # 如果遍历结束还没闭合
    return ""

system_prompt = ""

# 打开system_prompt.txt文件，读取内容
if os.path.isfile('expressionprompt.txt'):
    with open('expressionprompt.txt', 'r', encoding='utf-8') as f:
        system_prompt = f.read().strip()
else:
    system_prompt = "你是一个智能助手，帮助用户完成任务。"

# 对话函数，使用 Gemini API
def expression_get(user_input, temperature=0.8):
    try:
        # 调用 Gemini generate_content 接口
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=temperature
            ),
            # 传入消息
            contents = user_input
        )
    except Exception as e:
        print(f"Error: {e}")
        return "{\"response\": {\"content\": \"llmapi炸了喵...\"}}"

    # print(messege_body)

    ai_content = response.text.strip()

    # 解析与清洗响应
    ai_content = extract_json(ai_content)

    print(ai_content)

    return ai_content

if __name__ == "__main__":
    while True:
        user_text = input("您: ")
        if user_text.lower() in ['exit', 'quit']:
            break
        reply = expression_get(user_text)
        print(f"expression_get: {reply}")