import hashlib
import hmac
import base64
import json
import time
import pyaudio
import threading
from urllib.parse import quote
from websocket import create_connection, WebSocketConnectionClosedException
from webapi import smtu

# 打开config.json文件
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
    APP_ID = config.get('IFLYTEK_appid', 'your_app_id')
    API_KEY = config.get('IFLYTEK_apikey', 'your_api_key')
    UI_ENABLE = config.get('ui_enable', True)

END_TAG = json.dumps({"end": True})

# 音频配置
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
FRAMES_PER_BUFFER = 1280

result_content = ""

# 全局变量
stop_event = None
record_thread = None
recv_thread = None

time_during = 0
timer_running = False


#打开audio.txt文件
with open('audio.txt', 'r', encoding='utf-8') as f:
    audio_path = f.read().strip()

def generate_signa(app_id: str, api_key: str, ts: str) -> str:
    """
    根据appid、apikey和时间戳计算签名
    """
    md5 = hashlib.md5((app_id + ts).encode('utf-8')).hexdigest().encode('utf-8')
    signature = base64.b64encode(hmac.new(api_key.encode('utf-8'), md5, hashlib.sha1).digest())
    return quote(signature.decode('utf-8'))


def connect_ws(app_id: str, api_key: str) -> object:
    """
    建立WebSocket连接并返回ws对象
    """
    ts = str(int(time.time()))
    signa = generate_signa(app_id, api_key, ts)
    url = f"ws://rtasr.xfyun.cn/v1/ws?appid={app_id}&ts={ts}&signa={signa}"
    ws = create_connection(url)
    return ws


def recv_loop(ws):
    """
    接收服务器返回并处理实时识别结果。
    """
    global result_content, time_during
    try:
        while ws.connected:
            result = ws.recv()
            if not result:
                continue
            data = json.loads(result)
            action = data.get("action")
            if action == "started":
                print("Handshake success:", data)
            elif action == "result":
                # 解析data字段中的JSON数据
                result_data = json.loads(data.get("data", "{}"))
                # 提取cn.st结构
                st_data = result_data.get("cn", {}).get("st", {})
                # 提取type字段并转换为整数
                result_type = st_data.get("type", "-1")
                try:
                    result_type = int(result_type)
                except ValueError:
                    result_type = -1
                # 提取文本
                text = extract_text_from_json(st_data)
                if result_type == 0:
                    if(text == ""):
                        text = "无输入"
                    print(f"\nFinal result detected (type=0): {text}")
                    time_during = 0
                    #加入audio.txt后面
                    with open('audio.txt', 'a', encoding='utf-8') as f:
                        f.write(text)
                    result_content = text  # 直接保存最终结果（根据需求选择是否覆盖或追加）
                else:
                    print("Intermediate text:", text)
                    if(UI_ENABLE):
                        smtu("showmessage", time.time(), "按Enter键提交语音识别结果,按t键改文字输入,按esc键结束函数:\n" + text)
                    time_during = 0

            elif action == "error":
                print("Error details:", data)
                break
    except WebSocketConnectionClosedException:
        print("Connection closed by server")
    finally:
        ws.close()
        print("WebSocket connection closed")


def extract_text_from_json(st_data: dict) -> str:
    """
    从`cn.st`结构中的`rt`字段提取文本。
    """
    words = []
    for rt_entry in st_data.get("rt", []):
        for ws_entry in rt_entry.get("ws", []):
            for cw_entry in ws_entry.get("cw", []):
                words.append(cw_entry.get("w", ""))
    return "".join(words).strip()


def audio_stream(ws, stop_event):
    """
    打开麦克风采集音频并发送给服务器。
    """
    pa = pyaudio.PyAudio()
    stream = pa.open(format=FORMAT,
                     channels=CHANNELS,
                     rate=RATE,
                     input=True,
                     frames_per_buffer=FRAMES_PER_BUFFER)
    print("Start recording...")
    try:
        while not stop_event.is_set():
            chunk = stream.read(FRAMES_PER_BUFFER)
            ws.send(chunk)
    finally:
        # 发送结束标志并清理资源
        ws.send(END_TAG.encode('utf-8'))
        stream.stop_stream()
        stream.close()
        pa.terminate()
        print("Recording stopped.")

def stop_audio2text():
    global stop_event, record_thread, recv_thread
    if stop_event:
        # 通知采集线程停止
        stop_event.set()
    if record_thread:
        record_thread.join()
    if recv_thread:
        recv_thread.join()

timer_thread = None

def timeadd():
    global time_during, timer_running
    
    timer_running = True
    while timer_running:
        time_during += 1
        time.sleep(1)  # 暂停1秒

def start_timer():
    """启动计时器线程"""
    global timer_thread, timer_running
    timer_thread = threading.Thread(target=timeadd)
    timer_thread.daemon = True  # 设置为守护线程，主程序退出时会自动结束
    timer_thread.start()
    return timer_thread

def stop_timer():
    """停止计时器"""
    global timer_running, timer_thread
    timer_running = False
    timer_thread.join()
    timer_thread = None

def time_detect():
    global time_during
    return time_during

def audio2text():
    global result_content, stop_event, record_thread, recv_thread, time_during
    result_content = ""  # 重置结果
    time_during = 0
    
    # 建立WebSocket连接
    ws = connect_ws(APP_ID, API_KEY)
    
    # 启动接收线程
    recv_thread = threading.Thread(target=recv_loop, args=(ws,))
    recv_thread.start()
    
    # 启动音频采集线程
    stop_event = threading.Event()
    record_thread = threading.Thread(target=audio_stream, args=(ws, stop_event))
    record_thread.start()

    # # 开始计时
    # print("启动计时器...")
    # timer = start_timer()

    # time_detect_thread = start_time_detect()

    
    
    # input("Press Enter to stop recording...\n")
    # stop_event.set()
    
    # # 等待线程结束
    # record_thread.join()
    # recv_thread.join()
    return result_content


if __name__ == "__main__":
    final_text = audio2text()
    print("\nFinal recognized text:", final_text)