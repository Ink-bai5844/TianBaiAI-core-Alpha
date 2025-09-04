import json
import os
import subprocess
import time
from llmapi import api_chat
from tovitsapi import to_vits, play_audio_blocking
from memory.IOmemory import write_memory
from webapi import smtu
from expressionllmapi import expression_get


MODULE_DIR = os.path.dirname(os.path.dirname(__file__))

# 打开config.json文件
with open(os.path.join(MODULE_DIR, 'config.json'), 'r', encoding='utf-8') as f:
    config = json.load(f)
    VOICE_SYNTHESIS = config.get('voice_synthesis', True)
    UI_ENABLE = config.get('ui_enable', True)
    AUDIO_FILE_PATH = config.get('save_voice_path', os.path.join(MODULE_DIR, 'AudioTemp', 'output_audio.wav'))

def get_exp_json_to_id(json_str):
    expression_json = expression_get(json_str)
    # 解析并处理响应
    data = json.loads(expression_json)
    expression_id = data.get("id", -1)
    smtu("control", time.time(), "{\"control_object\": \"Live2DExpressionList\",\"control_value\": " + str(expression_id) + "}")

def execute_action(name,origin):
    if(name == "未分类"):
        if(VOICE_SYNTHESIS):
            if(not UI_ENABLE):
                play_audio_blocking()
            else:
                smtu("playmusic", time.time(), "{\"file\": \"" + AUDIO_FILE_PATH + "\", \"type\": 0, \"play_type\": 0}")
                # 获取音频时间
                audio_duration = subprocess.check_output(
                    ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', AUDIO_FILE_PATH]
                ).decode().strip()
                print(f"音频时长: {audio_duration}秒")
                # 等待音频播放完成
                audio_duration = max(float(audio_duration)-1, 0.0)
                time.sleep(audio_duration)

        # 调用API聊天函数
        response_json = api_chat(f"notfoundaction:{origin}")

        print(f"\nLink_bai：{response_json}")

        if(UI_ENABLE):
            # 发送消息给 Unity
            smtu("dialog", time.time(), response_json)
            get_exp_json_to_id(response_json)

        # 解析并处理响应
        data = json.loads(response_json)
        response = data.get("response", {})
        response_content = data.get("response", {}).get("content", "")
        emotion = data.get("response", {}).get("emotion", "")
        write_mem = response.get("writememory", {})
        write_time = write_mem.get("time", "")
        write_key = write_mem.get("key", "")
        write_content = write_mem.get("content", "")

        if(write_mem):
            # 写入记忆
            write_memory(write_time, write_key, write_content)
            print(f"写入记忆：时间: {write_time}, 键: {write_key}, 内容: {write_content}")

        if(VOICE_SYNTHESIS):
            to_vits(response_content, emotion)

        print(f"未定义操作:{origin}")
        return
    # 读取并解析action.json文件
    with open(os.path.join(MODULE_DIR, 'actions', 'action.json'), 'r', encoding='utf-8') as f:
        actions = json.load(f)
    
    # 查找匹配的action
    for action in actions:
        if action['name'] == name:
            # 执行所有open路径
            for path in action['open']:
                try:
                    os.startfile(path)  # 使用默认程序打开文件
                except Exception as e:
                    print(f"Error opening {path}: {e}")
            
            # 处理extra中的脚本
            extra = action.get('extra', '').strip()
            if extra:
                ext = os.path.splitext(extra)[1].lower()
                try:
                    if ext == '.py':
                        subprocess.run(['python', extra], shell=True)
                    elif ext == '.bat':
                        subprocess.run([extra], shell=True)
                    else:
                        print(f"Unsupported extra file type: {ext}")
                except Exception as e:
                    print(f"Error executing extra script {extra}: {e}")
            return
    
    # 如果未找到匹配的action
    raise ValueError(f"Action '{name}' not found in action.json.")