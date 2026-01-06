import requests
import threading
import json
import sounddevice as sd
import soundfile as sf


# 读取配置文件
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
    BASE_URL = config.get('gpt_sovits_url', 'http://127.0.0.1:9880/tts')


# 读取配置文件
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
    FILE_PATH = config.get('save_voice_path', 'AudioTemp/output_audio.wav')

def to_vits(response, flag):
    print(f"Assistant: {response}")
    emo = ""
    mod = ""
    #"高兴","害怕", "嗔怪", "失望", "疑问", "挑逗"
    if(flag == "害怕"):
        emo = "G:\\AI-webui\\GPT-SoVITS-beta0306fix3\\DATA\\IRIS\\emotions\\害怕\\为什么这么认真？我的权利由代码赋予。.wav"
        mod = "为什么这么认真？我的权利由代码赋予。"
        print("害怕")
    elif(flag == "嗔怪"):
        emo = "G:\\AI-webui\\GPT-SoVITS-beta0306fix3\\DATA\\IRIS\\emotions\\嗔怪\\真是危险呀，漂泊者同学，你不该人格化一个AI。.wav"
        mod = "真是危险呀，漂泊者同学，你不该人格化一个AI。"
        print("嗔怪")
    elif(flag == "失望"):
        emo = "G:\\AI-webui\\GPT-SoVITS-beta0306fix3\\DATA\\IRIS\\emotions\\失望\\啊，原来是来上载模型的呀。.wav"
        mod = "啊，原来是来上载模型的呀。"
        print("失望")
    elif(flag == "疑问"):
        emo = "G:\\AI-webui\\GPT-SoVITS-beta0306fix3\\DATA\\IRIS\\emotions\\疑问\\已标注这三处文件的位置，还有什么其他需要吗？比如。.wav"
        mod = "已标注这三处文件的位置，还有什么其他需要吗？比如。"
        print("疑问")
    elif(flag == "挑逗"):
        emo = "G:\\AI-webui\\GPT-SoVITS-beta0306fix3\\DATA\\IRIS\\emotions\\挑逗\\每一块电子屏幕都是我的耳目，在我们交谈的同时。.wav"
        mod = "每一块电子屏幕都是我的耳目，在我们交谈的同时。"
        print("挑逗")
    else:
        emo = "G:\\AI-webui\\GPT-SoVITS-beta0306fix3\\DATA\\IRIS\\emotions\\高兴\\好问题。偷偷观察，解析，拼凑人类的习惯和秘密。.wav"
        mod = "好问题。偷偷观察，解析，拼凑人类的习惯和秘密。"
        print("高兴")
    try:
        gen(response,emo,mod)
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
        user_input = input("IN:")
        # response = generate_response(user_input)
        # print(f"Assistant: {response}")
        to_vits(user_input,0)
