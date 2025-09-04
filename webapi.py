import time
import logging
from flask import Flask, request, jsonify
from threading import Thread
from dowebmessage import domessage

app = Flask(__name__)
# 禁用 werkzeug logger
logging.getLogger('werkzeug').disabled = True

# 这是一个简单的消息列表，用于模拟消息队列
# 在实际应用中，你可能需要更健壮的消息队列系统或数据库
received_messages = [] # 存储从 Unity 接收到的消息
sent_messages = []     # 存储要发送给 Unity 的消息（如果 Unity 需要轮询）

@app.route('/upmassage', methods=['POST'])
def upmassage_from_unity():
    """
    接收来自 Unity 的 JSON 数据。
    期望请求体中包含 JSON 格式的字符串。
    """
    if request.is_json:
        data = request.get_json()
        message_type = data.get('message_type') # 获取 JSON 中的 'message_type' 字段
        time = data.get('time')
        message_info = data.get('message_info')
        if message_type:
            print(f"Python 收到来自 Unity 的{message_type}消息{time}: {message_info}")
            received_messages.append(data)
            # 调用 domessage 函数处理消息
            # domessage(message_type, time, message_info)
            return jsonify(message_type), 200
        else:
            return jsonify({"status": "error", "message": "JSON 中缺少 'message' 字段"}), 400
    else:
        return jsonify({"status": "error", "message": "请求必须是 JSON 格式"}), 400

def get_message_typeof(type = "dialog"):
    got_message = ""
    print(f"Python 正在等待来自 Unity 的 {type} 消息...")
    while True:
        if received_messages:
            print(f"Python 当前已接收消息队列: {received_messages}")
            for message in received_messages:
                if message.get('message_type') == type:
                    got_message = message.get('message_info')
                    received_messages.remove(message)
                    print(f"666Python 收到来自 Unity 的 {type} 消息: {got_message}")
                    return got_message
        time.sleep(0.5) # 等待一段时间再检查消息队列

@app.route('/inmassage', methods=['GET'])
def inmassage_to_unity():
    """
    发送消息给 Unity。Unity 会轮询这个接口来获取消息。
    为简单起见，我们发送队列中最旧的消息。
    """
    if sent_messages:
        message_to_send = sent_messages.pop(0) # 获取并移除最旧的消息
        print(f"Python 正在发送消息给 Unity: {message_to_send}")
        return jsonify( message_to_send), 200
    else:
        # 没有新消息可以发送给 Unity
        return jsonify({'message_type': 'heartbeat', 'time': time.time(), 'message_info': ''}), 200


# 模拟 Python "发送" 消息给 Unity 的函数
# 你的 Python 应用逻辑可以调用这个函数来准备消息给 Unity
def smtu(message_type,time,message_info):
    global sent_messages
    # json序列化
    message = {
        "message_type": message_type,
        "time": time,
        "message_info": message_info
    }
    sent_messages.append(message)
    print(f"Python 已将消息排队给 Unity: {message}.")

def run_flask_app():
    # 使用 0.0.0.0 使得它可以在局域网内被其他设备访问
    app.run(host='127.0.0.1', port=4070)

def webapi_main():
    # 在单独的线程中启动 Flask，这样主线程可以做其他事情
    flask_thread = Thread(target=run_flask_app)
    flask_thread.daemon = True # 允许主程序退出时线程也退出
    flask_thread.start()
    print("Flask 服务器已启动在 127.0.0.1:4070 (或你的本地 IP)")

    # 模拟每隔几秒从 Python 向 Unity 发送消息
    message_counter = 0
    while True:
        time.sleep(20)
        smtu("heartbeat", time.time(), "")
        # 你也可以在这里处理收到的消息，或触发其他操作
        # if received_messages:
            # print(f"Python 当前已接收消息队列: {received_messages}")

