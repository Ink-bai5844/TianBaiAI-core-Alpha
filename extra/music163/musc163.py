import pyautogui
import pygetwindow as gw
import time
import re
import pyperclip
import os
import win32gui
import win32con

action = ""

def get_app_window_region(window_title="Alarms & Clock"):
    """获取目标应用程序窗口的屏幕区域"""
    try:
        win = gw.getWindowsWithTitle(window_title)[0]
        if not win.isActive:
            win.activate()
        time.sleep(0.5)  # 等待窗口激活
        
        # 返回区域坐标 (left, top, width, height)
        return (
            win.left,
            win.top,
            win.width,
            win.height
        )
    except IndexError:
        raise Exception(f"找不到标题包含 '{window_title}' 的窗口")

def click_in_window(image_path, region, confidence=0.9):
    """在指定窗口区域内查找并点击元素"""
    try:
        # 限制搜索区域并提高识别精度
        pos = pyautogui.locateOnScreen(
            image_path,
            region=region,
            confidence=confidence,
            grayscale=True
        )
        if pos:
            pyautogui.click(pyautogui.center(pos))
            return True
        return False
    except pyautogui.ImageNotFoundException:
        return False
    
def click_fullscreen(image_path, confidence=0.9):
    """在全屏范围内查找并点击元素"""
    try:
        pos = pyautogui.locateOnScreen(
            image_path,
            confidence=confidence,
            grayscale=True
        )
        if pos:
            pyautogui.click(pyautogui.center(pos))
            return True
        return False
    except pyautogui.ImageNotFoundException:
        return False
    
def bring_to_front(window_title):
    window = win32gui.FindWindow(None, window_title)
    if window:
        # 如果窗口最小化，先恢复
        if win32gui.IsIconic(window):
            win32gui.ShowWindow(window, win32con.SW_RESTORE)
        # 将窗口置于前台
        win32gui.SetForegroundWindow(window)
    else:
        print(f"未找到标题为 '{window_title}' 的窗口")

#读取tmp.txt文件
with open('tmp.txt', 'r', encoding='utf-8') as f:
    action = f.read()

#确保网易云音乐窗口处于活动状态
os.startfile("E:\\CloudMusic\\cloudmusic.exe")

# bring_to_front("NetEase Cloud Music")

#若有"歌单"则执行
if "歌单" in action:
    time.sleep(5)
    # window_region = get_app_window_region("NetEase Cloud Music")

    if not click_fullscreen('extra/music163/001.png'):
        raise Exception("找不到歌单按钮")
    time.sleep(1)

    if not click_fullscreen('extra/music163/002.png'):
        raise Exception("找不到播放按钮")


if(("暂停" in action) or ("停止" in action) and ("歌单" not in action)):
    # 暂停音乐
    pyautogui.hotkey('ctrl', 'alt', 'p')
    time.sleep(0.5)

if(("播放" in action) and ("歌单" not in action) and ("暂停" not in action) and ("喜欢" not in action) and ("收藏" not in action)):
    time.sleep(5)
    # 播放音乐
    pyautogui.hotkey('ctrl', 'alt', 'p')
    time.sleep(0.5)

if("上一首" in action and "歌单" not in action):
    # 上一首音乐
    pyautogui.hotkey('ctrl', 'alt', 'left')
    time.sleep(0.5)

if(("下一首" in action or "切换歌曲" in action) and "歌单" not in action):
    # 下一首音乐
    pyautogui.hotkey('ctrl', 'alt', 'right')
    time.sleep(0.5)

if(("喜欢" in action or "收藏" in action) and "歌单" not in action):
    # 喜欢音乐
    pyautogui.hotkey('ctrl', 'alt', 'k')
    time.sleep(0.5)

if("歌词" in action and "歌单" not in action):
    # 显示歌词
    pyautogui.hotkey('ctrl', 'alt', 'd')
    time.sleep(0.5)