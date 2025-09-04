import pyautogui
import pyperclip
import time

pyautogui.hotkey('win', 's')
time.sleep(0.5)

pyperclip.copy("设置")           # 中文复制到剪贴板
pyautogui.hotkey('ctrl', 'v')   # 粘贴
time.sleep(0.5)

pyautogui.press('enter')

