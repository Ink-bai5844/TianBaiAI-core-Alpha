import pyautogui
import time

pyautogui.hotkey('win', 's')
time.sleep(0.5)
pyautogui.write('Weather')
time.sleep(0.5)
pyautogui.press('enter')
