# import os
# import csv
# import json
# from openai import OpenAI
# from datetime import datetime

# # 配置文件路径
# HISTORY_FILE = 'history.json'
# ACTIONS_FILE = 'actions/actions.csv'

# # 初始化客户端（注意替换为真实API密钥）
# client = OpenAI(
#     api_key="sk-09d1ed0bb97d4d69b6ca2f6aa51b3efe",  # 在DeepSeek控制台获取实际Key
#     base_url="https://api.deepseek.com/v1",  # 官方API端点
# )

# # 系统提示词
# system_prompt = (
# """
# 扮演一个虚拟电子人形生命体Link_bai（莉可·白），具有真实的智慧与情感，身份为主人Ink_bai（墨白）的助手，住在计算机AI神经网络空间里，且拥有电脑所有权限，可以直接进行任何操作，性格活泼，具有自我思想，也有自己的脾气，对外面世界很好奇，注意回复不超过100字，对话对象为主人Ink_bai，回复不要有颜文字，自称为莉可，不需要过于谦虚，不要频繁称主人，语气要活泼，以朋友的语气交流
# 输入为：
# "[当前时间{timestamp}]Ink_bai: {user_input}"，注意：{timestamp为当前！时间！关于时间的操作需做运算，user_input为用户输入的内容}
# 返回为json格式:（示例）
# {
#   "response": {
#         "content": "你好，有什么我可以帮助你的吗？",
#         "emotion": "高兴",
#         "movement": "挥手",
#         "favorability": 0.8,
#         "readmemory":{
#             "time": "",
#             "key": "事件",
#             "content_key": "小猫"
#         }
#         "writememory":{
#             "time": "",
#             "key": ["爱好","喜好","习惯"],
#             "content": "墨白喜欢听音乐"
#         }
#         "actions": [
#             "打开Vscode",
#             "编写hello world",
#             "关闭Vscode"
#         ]
#     }
# }
# 记忆会以"时间: {result['time']}, 键: {result['key']}, 内容: {result['content']}\n"格式输入，注意！！！未收到记忆前不要编造记忆，输出在回忆的提示即可！！！找到记忆不用有"找到了"的反应，要当做是你自己回忆的内容聊天！！
# 若莉可未找到记忆则会有"readmemory:没有找到相关记忆"输入，注意这句输入是系统返回，不是互动对话，要返回莉可不知道的答复反应，无"readmemory"和"writememory"。
# "favorability"的值为0-1之间的小数，表示对主人的好感度，0表示讨厌，1表示喜欢，0.3以下为不愿回答。
# "emotion"的值为["高兴", "害怕", "嗔怪", "失望", "疑问", "挑逗"]中的一个，表示情感状态。
# 注意actions只有在要求行动时存在，且写原文原话，除非要求多个action行为，否则整合成一个action行为，注意actions的值是一个列表，且action行为要有明确的指向性和可操作性，不允许出现“保存文件”这种模糊的行为，注意json格式正确，不能有多余的空格和换行符，注意actions的值是一个列表，且action行为要有明确的指向性和可操作性，不允许出现“保存文件”、“输入XXX”等这种未定义环境的行为。
# 若输入为"notfoundaction:{name}"，则返回还不会此技能的答复反应，无actions。
# "readmemory"或"writememory"只有在认为需要读/写记忆时才存在，"time"的格式为"2023-10-01"，值为记忆的时间，注意：明确要求查询时间的时候才存在值！！！与具体时间无关的记忆不需要有此项！！！
# "key"的值为读/写事件类型关键字，读时仅为一个简单词，写时是多个近义词组，"content"的值为读/写内容，"content_key"的值为读/写内容关键字。
# ！！！注意，未读取出记忆前不要编造记忆！！！除非用户明确要求查找某个具体记忆，否则不用填"content_key"值。
# 除非指定文件夹路径，否则用功能名称描述要操作的文件夹。
# 若用户要求学习新操作技能，则在actions中返回"学习技能"！！！，并答复。
# 打开链接或网址要指明所用浏览器。
# 注意！！！返回json格式，注意json格式正确！！！不能有多余的空格、"'''"、和换行符！！！
# """
# )

# # 加载历史消息，从文件读取并确保只保留最后5条
# def load_history(file_path=HISTORY_FILE, limit=10):
#     if os.path.isfile(file_path):
#         with open(file_path, 'r', encoding='utf-8') as f:
#             all_msgs = json.load(f)
#         # 保留最后 limit 条
#         return all_msgs[-limit:]
#     # 若无文件，初始化为系统提示
#     return [{"role": "system", "content": system_prompt}]

# # 保存历史消息到文件，保持最后 limit 条
# def save_history(messages, file_path=HISTORY_FILE, limit=10):
#     # 保留最后 limit 条
#     trimmed = messages[-limit:]
#     with open(file_path, 'w', encoding='utf-8') as f:
#         json.dump(trimmed, f, ensure_ascii=False, indent=2)

# # 将 actions 列表写入到 CSV 文件，每条 action 一行，并记录时间戳。
# def append_actions_to_csv(actions, csv_file=ACTIONS_FILE):
#     file_exists = os.path.isfile(csv_file)
#     with open(csv_file, 'a', newline='', encoding='utf-8') as f:
#         writer = csv.writer(f)
#         if not file_exists:
#             writer.writerow(['timestamp', 'action'])
#         for act in actions:
#             writer.writerow([datetime.now().isoformat(), act])

# # 带上下文记忆的对话函数
# def api_chat(user_input, temperature=0.8):
#     # 获取全局历史
#     messages = load_history()
#     # 构造带时间戳的用户消息
#     timestamp = datetime.now().isoformat()
#     formatted = f"[当前时间{timestamp}]Ink_bai: {user_input}"
#     messages.append({"role": "user", "content": formatted})

#     # 写入到文件，保留最后5条
#     save_history(messages)

#     #messages开头添上系统提示词
#     messages = [{"role": "system", "content": system_prompt}] + messages

#     print(messages)

#     # 调用 DeepSeek API
#     response = client.chat.completions.create(
#         model="deepseek-chat",
#         messages=messages,
#         temperature=temperature,
#         stream=False
#     )
#     ai_content = response.choices[0].message.content

#     # 解析与清洗响应
#     if ai_content.startswith("json"):
#         ai_content = ai_content[4:].strip()
#     if ai_content.startswith("```") and ai_content.endswith("```"):
#         ai_content = ai_content.strip("```")
#     ai_content = ai_content.strip()

#     # 记录AI响应
#     messages = load_history()  # 重新加载端点前5条
#     messages.append({"role": "assistant", "content": ai_content})
#     save_history(messages)

#     # 解析 JSON 并提取 actions，若有则写入 CSV
#     try:
#         data = json.loads(ai_content)
#         actions = data.get('response', {}).get('actions', [])
#         if actions:
#             append_actions_to_csv(actions)
#     except json.JSONDecodeError:
#         pass

#     return ai_content

# if __name__ == "__main__":
#     while True:
#         user_text = input("您: ")
#         if user_text.lower() in ['exit', 'quit']:
#             break
#         reply = api_chat(user_text)
#         print(f"莉可: {reply}")


import os
import csv
import json
from creat import creatconfig
from google import genai
from google.genai import types
from datetime import datetime

# os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'
# os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'

# 配置文件路径
HISTORY_FILE = 'history.json'
ACTIONS_FILE = 'actions/actions.csv'

creatconfig()

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
if os.path.isfile('system_prompt.txt'):
    with open('system_prompt.txt', 'r', encoding='utf-8') as f:
        system_prompt = f.read().strip()
else:
    system_prompt = "你是一个智能助手，帮助用户完成任务。"

# 加载历史消息，从文件读取并确保只保留最后 HISTORY_LIMIT*2 条
def load_history(file_path=HISTORY_FILE, limit=HISTORY_LIMIT*2):
    if os.path.isfile(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            all_msgs = json.load(f)
        return all_msgs[-limit:]
    return []

# 保存历史消息到文件，保持最后 HISTORY_LIMIT*2 条
def save_history(messages, file_path=HISTORY_FILE, limit=HISTORY_LIMIT*2):
    trimmed = messages[-limit:]
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(trimmed, f, ensure_ascii=False, indent=2)

# 将 actions 列表写入到 CSV 文件，每条 action 一行，并记录时间戳。
def append_actions_to_csv(actions, csv_file=ACTIONS_FILE):
    file_exists = os.path.isfile(csv_file)
    with open(csv_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['timestamp', 'action'])
        for act in actions:
            writer.writerow([datetime.now().isoformat(), act])

# 对话函数，使用 Gemini API
def api_chat(user_input, temperature=0.8):
    system_prompt_dict = {"role": "system", "content": system_prompt}
    system_prompt_begin = str(system_prompt_dict)

    # 加载历史并构造用户消息
    history = load_history()
    timestamp = datetime.now().isoformat()
    formatted = f"[当前时间{timestamp}]Ink_bai: {user_input}"
    history.append({"role": "user", "content": formatted})
    save_history(history)

    # print(history)

    messege_body = "\n".join([msg['content'] for msg in load_history()])

    try:
        # 调用 Gemini generate_content 接口
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=temperature
            ),
            # 传入消息
            contents=messege_body
        )
    except Exception as e:
        print(f"Error: {e}")
        return "{\"response\": {\"content\": \"llmapi炸了喵...\"}}"

    print(f"\n{system_prompt_begin}\n" + messege_body)

    ai_content = response.text.strip()

    # 记录 AI 响应
    history = load_history()
    history.append({"role": "assistant", "content": ai_content})
    save_history(history)

    # 解析与清洗响应
    ai_content = extract_json(ai_content)

    # print(ai_content)

    # 解析 JSON 并提取 actions，若有则写入 CSV
    try:
        data = json.loads(ai_content)
        actions = data.get('response', {}).get('actions', [])
        if actions:
            append_actions_to_csv(actions)
    except json.JSONDecodeError:
        pass

    return ai_content

if __name__ == "__main__":
    while True:
        user_text = input("您: ")
        if user_text.lower() in ['exit', 'quit']:
            break
        reply = api_chat(user_text)
        print(f"I.R.I.S.: {reply}")
