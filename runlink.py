import json
import time
import os
import threading
import keyboard
import subprocess
import queue
import random
from creat import creatconfig, creatmemory
from webapi import webapi_main, smtu, get_message_typeof
from actions.classcut import classify_action
from actions.actions import execute_action
from llmapi import api_chat
from actions.classcut import load_rules
from tovitsapi import to_vits, play_audio_blocking, play_audio_stream
from memory.IOmemory import read_memory, write_memory
from rtasr_python3_demo import audio2text, stop_audio2text, start_timer, stop_timer, time_detect
from wake_up.runwake import runwake
from expressionllmapi import expression_get

class_rules_file='actions/classification_rules.json'
rules = load_rules(class_rules_file)

creatconfig()
creatmemory()

# 打开config.json文件
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
    WAKE_OPEN = config.get('wake_word', True)
    VOICE_SYNTHESIS = config.get('voice_synthesis', True)
    VOICE_INPUT = config.get('voice_input', True)
    UI_ENABLE = config.get('ui_enable', True)
    AUDIO_FILE_PATH = config.get('save_voice_path', 'AudioTemp/output_audio.wav')

#打开tmp.txt
with open('tmp.txt', 'r', encoding='utf-8') as f:
    system_prompt = f.read()

#打开audio.txt
with open('audio.txt', 'r', encoding='utf-8') as f:
    audio_path = f.read().strip()

def get_random_wav_file(folder_path="BeginAudio"):
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"文件夹 '{folder_path}' 不存在")
    
    # 获取文件夹中所有.wav文件
    wav_files = [f for f in os.listdir(folder_path) 
                if f.lower().endswith('.wav') and os.path.isfile(os.path.join(folder_path, f))]
    
    # 如果没有找到.wav文件
    if not wav_files:
        return None
    
    # 随机选择一个文件
    selected_file = random.choice(wav_files)
    
    # 返回完整路径
    return os.path.join(folder_path, selected_file)

# 全局按键队列
key_queue = queue.Queue()

# 按键事件回调，将按键名称放入队列
def _on_key_event(event):
    if event.event_type == 'down':
        # event.name 是按键的字符串表示
        key_queue.put(event.name)

def hybrid_getch():
    """
    混合获取按键:
      1. 优先从全局钩子队列获取按键事件,
      2. 若无, 再检查模拟队列(key_queue),
      3. 若都无, 短暂休眠后重试。
    即使程序失去焦点也能捕获按键.
    """
    while True:
        # 优先获取全局钩子产生的按键
        try:
            key = key_queue.get_nowait()
            key_queue.queue.clear()  # 清空队列，避免重复读取
            return key
        except queue.Empty:
            pass

        time.sleep(0.01)  # 降低CPU占用

time_flag = 0
stop_flag = 0
timer = None
timer_thread = None
actions = []

def start_time_detect():
    # 启动时间监测
    global timer_thread
    timer_thread = threading.Thread(target=time_detect_while)
    timer_thread.daemon = True  # 设置为守护线程，主程序退出时会自动结束
    timer_thread.start()
    return timer_thread

def time_detect_while():
    global time_flag, stop_flag
    while not stop_flag:
        time_during = time_detect()
        print(f"当前时间：{time_during}秒")
        time.sleep(1)  # 每1秒显示一次
        if(time_during > 5):
            time_flag = 1
            key_queue.put('enter')  # 模拟Enter键
            keyboard.unhook_all()  # 关闭全局钩子
            break

def stop_time_detect():
    global timer_thread
    if timer_thread:
        timer_thread.join()
        timer_thread = None

def get_exp_json_to_id(json_str):
    expression_json = expression_get(json_str)
    # 解析并处理响应
    data = json.loads(expression_json)
    expression_id = data.get("id", -1)
    smtu("control", time.time(), "{\"control_object\": \"Live2DExpressionList\",\"control_value\": " + str(expression_id) + "}")

# 主运行逻辑
def main():
    global time_flag, stop_flag, actions
    print("欢迎使用 Link_bai（输入 '退出' 结束对话）")
    
    while True:
        user_input = ""
        # user_input = input("\nInk_bai：")
        # if user_input.lower() in ["退出", "exit"]:
        #     print("会话结束。再见~")
        #     break
        if(VOICE_INPUT):
            #清空audio.txt
            with open('audio.txt', 'w', encoding='utf-8') as f:
                f.write("")

            #并行线程运行audio2text()
            audio2text()
            # 开始计时
            print("启动计时器...")
            stop_flag = 0
            timer = start_timer()
            time_detect_thread = start_time_detect()
            
            while True:
                print("\n按Enter键提交语音识别结果,按t键改文字输入,按esc键结束函数:")
                if(UI_ENABLE):
                    smtu("showmessage", time.time(), "按Enter键提交语音识别结果,按t键改文字输入,按esc键结束函数:")

                # 安装全局钩子
                keyboard.hook(_on_key_event)

                key = hybrid_getch() # 使用自定义的getch

                print(f"按下的键: {key}")

                # 关闭全局钩子
                keyboard.unhook_all()
                
                if key == 't' or key == b't':
                    time_flag = 0
                    stop_flag = 1
                    stop_audio2text()
                    stop_timer()
                    stop_time_detect()
                    if(not UI_ENABLE):
                        user_input = input("Ink_bai：")
                    else:
                        smtu("control", time.time(), "{\"control_object\": \"dialoginput\",\"control_value\": 1}")
                        user_input = get_message_typeof()
                        smtu("control", time.time(), "{\"control_object\": \"dialoginput\",\"control_value\": 0}")
                    break
                # Enter
                elif key == "enter" or key == b'\r':
                    time_flag = 0
                    stop_flag = 1
                    stop_audio2text()
                    stop_timer()
                    stop_time_detect()
                    try:
                        with open('audio.txt', 'r', encoding='utf-8') as f:
                            user_input = f.read().strip()
                    except FileNotFoundError:
                        print("错误：audio.txt 未找到。")
                        user_input = ""
                    if(UI_ENABLE):
                        smtu("showmessage", time.time(), "输入:" + user_input)
                    break
                elif key == "esc" or key == b'\x1b':
                    time_flag = 0
                    stop_flag = 1
                    stop_audio2text()
                    stop_timer()
                    stop_time_detect()
                    return
                else:
                    time_flag = 0
                    stop_flag = 1
                    print("无效输入，请重新按键。")

            if(time_flag):
                time_flag = 0
                stop_flag = 1
                print("时间到，停止语音识别。")
                stop_audio2text()
                stop_timer()
                stop_time_detect()
                try:
                    with open('audio.txt', 'r', encoding='utf-8') as f:
                        user_input = f.read().strip()
                except FileNotFoundError:
                    print("错误：audio.txt 未找到。")
                    user_input = ""

        else:
            user_input = input("\n(输入exit退出)Ink_bai：")
            if user_input.lower() in ["退出", "exit"]:
                print("会话结束。再见~")
                break

        # 调用API聊天函数
        response_json = api_chat(user_input)

        print(f"\nLink_bai：{response_json}")

        if(UI_ENABLE):
            # 发送消息给 Unity
            smtu("dialog", time.time(), response_json)
            get_exp_json_to_id(response_json)

        # 解析并处理响应
        data = json.loads(response_json)
        response = data.get("response", {})

        response_content = response.get("content", "")
        emotion = response.get("emotion", "")
        movement = response.get("movement", "")
        favorability = response.get("favorability", 0.0)
        actions = response.get("actions", [])

        read_mem = response.get("readmemory", {})
        read_time = read_mem.get("time", "")
        read_key = read_mem.get("key", "")

        write_mem = response.get("writememory", {})
        write_time = write_mem.get("time", "")
        write_key = write_mem.get("key", "")
        write_content = write_mem.get("content", "")

        read_results = []

        if(VOICE_SYNTHESIS):
            to_vits(response_content, emotion)

        if(read_mem):
            if(VOICE_SYNTHESIS):
                if(not UI_ENABLE):
                    play_audio_stream()
                else:
                    smtu("playmusic", time.time(), "{\"file\": \"" + AUDIO_FILE_PATH + "\", \"type\": 0, \"play_type\": 0}")
            # 读取记忆
            read_results = read_memory(time=read_time, key=read_key)
            mem_strs = ""
            if read_results:
                for result in read_results:
                    print(f"读取到记忆：时间: {result['time']}, 键: {result['key']}, 内容: {result['content']}")
                    mem_strs += f"时间: {result['time']}, 键: {result['key']}, 内容: {result['content']}\n"
                # 处理读取到的记忆
                response_json2 = api_chat(f"readmemory:{mem_strs}")
                print(f"\nLink_bai：{response_json2}")

                if(UI_ENABLE):
                    # 发送消息给 Unity
                    smtu("dialog", time.time(), response_json2)
                    get_exp_json_to_id(response_json2)

                # 解析并处理响应
                data2 = json.loads(response_json2)
                response2 = data2.get("response", {})

                response_content2 = response2.get("content", "")
                emotion2 = response2.get("emotion", "")
                movement2 = response2.get("movement", "")
                favorability2 = response2.get("favorability", 0.0)
                actions = response2.get("actions", []) #整合行为
                if(VOICE_SYNTHESIS):
                    to_vits(response_content2, emotion2)

            else:
                print("没有找到相关记忆")
                response_json2 = api_chat("readmemory:没有找到相关记忆")
                print(f"\nLink_bai：{response_json2}")

                if(UI_ENABLE):
                    # 发送消息给 Unity
                    smtu("dialog", time.time(), response_json2)
                    get_exp_json_to_id(response_json2)

                # 解析并处理响应
                data2 = json.loads(response_json2)
                response2 = data2.get("response", {})

                response_content2 = response2.get("content", "")
                emotion2 = response2.get("emotion", "")
                movement2 = response2.get("movement", "")
                favorability2 = response2.get("favorability", 0.0)
                actions = response2.get("actions", [])
                if(VOICE_SYNTHESIS):
                    to_vits(response_content2, emotion2)


        if(write_mem):
            # 写入记忆
            write_memory(write_time, write_key, write_content)
            print(f"写入记忆：时间: {write_time}, 键: {write_key}, 内容: {write_content}")

        if actions and not read_mem:
            for action in actions:
                with open('tmp.txt', 'w', encoding='utf-8') as f:
                    f.write("")
                with open('tmp.txt', 'a', encoding='utf-8') as f:
                    f.write(f"{action}\n")
                classified_action = classify_action(action, rules)
                execute_action(classified_action,action)

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
        
        time.sleep(1)
        continue

if __name__ == "__main__":
    if(UI_ENABLE):
        webapi_main_thread = threading.Thread(target=webapi_main)
        webapi_main_thread.daemon = True
        webapi_main_thread.start()
    if(WAKE_OPEN):
        while True:
            try:
                if(UI_ENABLE):
                    smtu("showmessage", time.time(), "莉可在这里哦~")
                runwake()
                play_audio_blocking(get_random_wav_file())
                main()
            except Exception as e:
                print(f"发生错误: {e}")
                break
    else:
        try:
            main()
        except Exception as e:
            print(f"发生错误: {e}")
            pass
        