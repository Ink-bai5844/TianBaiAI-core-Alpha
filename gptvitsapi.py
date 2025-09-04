import requests
import io
import sounddevice as sd
import scipy.io.wavfile as wav

# 设置 API 端点
BASE_URL = "http://127.0.0.1:9880/tts"


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


# 播放音频流
def play_audio_stream(audio_data):
    audio_stream = io.BytesIO(audio_data)
    sample_rate, audio_data = wav.read(audio_stream)
    sd.play(audio_data, samplerate=sample_rate)
    sd.wait()


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

# 生成语音
def gen(totext,ref_audio_path,prompt_text):
    audio_data = generate_speech_get(totext, text_lang, ref_audio_path, prompt_text, prompt_lang, text_split_method,
                                 batch_size, media_type, streaming_mode)
    if audio_data:
        # 保存音频
        file_path = 'AudioTemp\output_audio.wav'
        with open(file_path, 'wb') as file:
            file.write(audio_data)

        print(f"Audio saved to {file_path}")

        # 播放音频
        play_audio_stream(audio_data)





