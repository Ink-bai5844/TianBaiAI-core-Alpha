import os

# 调取当前绝对路径
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))

def creatconfig():
    # 检查 config.json 是否存在
    if not os.path.exists('config.json'):
        # 创建 config.json 并写入默认配置
        default_config = '''{
            "name": "Tian_bai",
            "version": "1.0.2",
            "UI_enable": true,
            "Project_Path": "{MODULE_DIR}",
            "Gemini_key": "你的Gemini API Key",
            "history_length": 6,
            "wake_word": true,
            "voice_input": true,
            "voice_synthesis": true,
            "save_voice_path": "{MODULE_DIR}/AudioTemp/output_audio.wav",
            "IFLYTEK_appid": "你的讯飞AppID",
            "IFLYTEK_apikey": "你的讯飞API Key",
            "gpt_sovits_url": "http://127.0.0.1:9880/tts",
            "wake_access_key": "你的porcupine API Key"
        }'''.replace("{MODULE_DIR}", MODULE_DIR).replace("\\", "/")
        with open('config.json', 'w', encoding='utf-8') as f:
            f.write(default_config)
        print("已创建默认配置文件 config.json，请根据需要修改后重新运行程序。")

def creatmemory(): # memory文件夹及文件
    memory_dir = os.path.join(MODULE_DIR, 'memory')
    if not os.path.exists(memory_dir):
        os.makedirs(memory_dir)
    
    memory_file = os.path.join(memory_dir, 'memory.csv')
    if not os.path.exists(memory_file):
        with open(memory_file, 'w', encoding='utf-8') as f:
            f.write('time\n')
    
    alias_file = os.path.join(memory_dir, 'alias_mapping.csv')
    if not os.path.exists(alias_file):
        with open(alias_file, 'w', encoding='utf-8') as f:
            f.write('alias,main_key\n')
    
    print("已创建 memory 文件夹及必要的 CSV 文件。")

if __name__ == "__main__":
    # creatconfig()
    creatmemory()