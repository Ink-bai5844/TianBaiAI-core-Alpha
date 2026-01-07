import requests
import threading
import json
import sounddevice as sd
import soundfile as sf
import os

# 读取配置文件
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
    BASE_URL = config.get('gpt_sovits_url', 'http://127.0.0.1:9880/tts')
    FILE_PATH = config.get('save_voice_path', 'AudioTemp/output_audio.wav')
    SOVITS_MODEL = config.get('sovits_model', 'G:/AI-webui/GPT-SoVITS-beta0306fix3/SoVITS_weights/IRIS_e12_s132.pth')
    GPT_MODEL = config.get('gpt_model', 'G:/AI-webui/GPT-SoVITS-beta0306fix3/GPT_weights/IRIS-e15.ckpt')

def load_emotion_config(config_path='emotions_config.json'):
    """读取并解析情感配置文件"""
    if not os.path.exists(config_path):
        print(f"Warning: Config file {config_path} not found!")
        return None
        
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return None

EMOTION_CONFIG = load_emotion_config()

def set_gpt_weights():
    root_url = BASE_URL.replace("/tts", "")
    url = f"{root_url}/set_gpt_weights"
    params = {"weights_path": GPT_MODEL} 
    response = requests.get(url, params=params)

def set_sovits_weights():
    root_url = BASE_URL.replace("/tts", "")
    url = f"{root_url}/set_sovits_weights"
    params = {"weights_path": SOVITS_MODEL} 
    response = requests.get(url, params=params)

def to_vits(response, flag):
    print(f"Assistant: {response}")
    
    if not EMOTION_CONFIG:
        print("Error: Configuration not loaded.")
        return None

    # 获取基础路径和默认情绪
    base_path = EMOTION_CONFIG.get("base_path", "")
    default_key = EMOTION_CONFIG.get("default_emotion", "高兴")
    emotions_data = EMOTION_CONFIG.get("emotions", {})

    current_key = flag if flag in emotions_data else default_key
    
    data = emotions_data.get(current_key)
    
    emo_path = os.path.join(base_path, data['file'])
    mod_text = data['text']

    print(f"当前情绪: {current_key}")

    try:
        gen(response, emo_path, mod_text) 
    except Exception as e:
        print(f"Error generating speech: {e}")
        return None

# 调用 API 生成语音（GET 请求）
def generate_speech_get(text, text_lang, ref_audio_path, prompt_text, prompt_lang, text_split_method, batch_size,
                        media_type, streaming_mode):
    params = {
        "text": text,
        "text_lang": text_lang,
        "ref_audio_path": ref_audio_path,
        "prompt_text": prompt_text,
        "prompt_lang": prompt_lang,
        "text_split_method": text_split_method,
        "batch_size": batch_size,
        "media_type": media_type,
        "streaming_mode": streaming_mode
    }

    response = requests.get(BASE_URL, params=params, stream=True)

    if response.status_code == 200:
        return response.content
    else:
        print("Error:", response.json())
        return None


def play_audio_stream(path = FILE_PATH):
    """非阻塞方式播放音频流（多线程实现）（FILE_PATH）"""
    def _play_audio():
        # 使用soundfile读取音频数据，它能更好地处理BytesIO
        audio_data_array, sample_rate = sf.read(path)
        sd.play(audio_data_array, samplerate=sample_rate)
        sd.wait()  # 等待音频播放完成
    
    # 创建并启动播放线程
    play_thread = threading.Thread(target=_play_audio)
    play_thread.daemon = True  # 设置为守护线程，主程序退出时自动结束
    play_thread.start()

def play_audio_blocking(path = FILE_PATH):
    """阻塞方式播放音频流(FILE_PATH)"""
    # 使用soundfile读取音频数据，它能更好地处理BytesIO
    audio_data_array, sample_rate = sf.read(path)
    sd.play(audio_data_array, samplerate=sample_rate)
    sd.wait()  # 等待音频播放完成


# 示例参数
text = "最喜欢墨白了！"
text_lang = "zh"
# ref_audio_path = "G:\\AI-webui\\GPT-SoVITS-beta0306fix3\\DATA\\sui\\emotions\\高兴\\良爷的这个礼物，我很喜欢。良。.wav"
# prompt_text = "良爷的这个礼物，我很喜欢。良。"
prompt_lang = "zh"
text_split_method = "cut5"
batch_size = 1
media_type = "wav"
streaming_mode = "false"

audio_data = None

# 生成语音
def gen(totext,ref_audio_path,prompt_text):
    global audio_data
    audio_data = generate_speech_get(totext, text_lang, ref_audio_path, prompt_text, prompt_lang, text_split_method,
                                 batch_size, media_type, streaming_mode)
    if audio_data:
        # 保存音频
        with open(FILE_PATH, 'wb') as file:
            file.write(audio_data)

        print(f"Audio saved to {FILE_PATH}")

        # 播放音频
        # play_audio_stream(audio_data)
        # play_audio_blocking(audio_data)

        


if __name__ == '__main__':
    while(True):
        set_gpt_weights()
        set_sovits_weights()
        user_input = input("IN:")
        # response = generate_response(user_input)
        # print(f"Assistant: {response}")
        to_vits(user_input,0)
