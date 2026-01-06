import pvporcupine
from pvrecorder import PvRecorder
import os
import json

MODULE_DIR = os.path.dirname(os.path.dirname(__file__))

# 读取config.json文件
with open(os.path.join(MODULE_DIR, 'config.json'), 'r', encoding='utf-8') as f:
    config = json.load(f)
    ACCESS_KEY = config.get('wake_access_key', '')

keywords = ["IRIS"]

porcupine = pvporcupine.create(
  access_key=ACCESS_KEY,
  keyword_paths=[os.path.join(MODULE_DIR, 'wake_up/model/Iras_en_windows_v4_0_0.ppn')],
  model_path=os.path.join(MODULE_DIR, 'wake_up/model/porcupine_params.pv')
)

recoder = PvRecorder(device_index=-1, frame_length=porcupine.frame_length)

def runwake():
    print("Listening for wake word...")
    recoder.start()
    while True:
        keyword_index = porcupine.process(recoder.read())
        if keyword_index >= 0:
            print(f"Detected {keywords[keyword_index]}")
            recoder.stop()
            return keyword_index
    
        
def stop_wake():
    porcupine.delete()
    recoder.delete()

if __name__ == "__main__":
    runwake()
    stop_wake()


# import pvporcupine
# from pvrecorder import PvRecorder


# access_key = "GFtcAMVarwEPN2lexjWdOQJn8mk5Q3x3Ii9XW6A1KFKD76/9Gum37Q=="

# keywords = ["Link_bai"]

# porcupine = pvporcupine.create(
#   access_key=access_key,
#   keyword_paths=['wake_up/model/Link-bai_en_windows_v3_0_0.ppn'],
#   model_path='wake_up/model/porcupine_params.pv'
# )

# recoder = PvRecorder(device_index=-1, frame_length=porcupine.frame_length)

# print("Listening for wake word...")

# try:
#     recoder.start()
#     while True:
#         keyword_index = porcupine.process(recoder.read())
#         if keyword_index >= 0:
#             print(f"Detected {keywords[keyword_index]}")
# except KeyboardInterrupt:
#     recoder.stop()
# finally:
#     porcupine.delete()
#     recoder.delete()
