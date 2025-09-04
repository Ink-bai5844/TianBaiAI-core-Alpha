import pyautogui
import pygetwindow as gw
import time
import re
import pyperclip

class AlarmSetter:
    def __init__(self, window_title="时钟"):
        self.window = self._get_window(window_title)
        self.region = (
            self.window.left,
            self.window.top,
            self.window.width,
            self.window.height
        )
        # 预定义相对坐标系数（基于窗口大小的比例）
        self.time_input_offsets = {
            'hour': (0.45, 0.35), 
            'minute': (0.55, 0.35),
            'save': (0.45, 0.78)  # 保存按钮的相对位置
        }

    def _get_window(self, title):
        """获取并激活目标窗口"""
        try:
            win = gw.getWindowsWithTitle(title)[0]
            # 恢复最小化状态
            if win.isMinimized:
                win.restore()
                time.sleep(0.5)
            # 激活窗口
            if not win.isActive:
                win.activate()
                time.sleep(0.5)
            return win
        except IndexError:
            raise Exception(f"Window '{title}' not found")

    def click_in_window(self, image_path, region=None, confidence=0.9):
        """在指定窗口区域内查找并点击元素"""
        search_region = region or self.region
        # 给UI一些响应时间
        time.sleep(0.5)
        pos = pyautogui.locateOnScreen(
            image_path,
            region=search_region,
            confidence=confidence,
            grayscale=True
        )
        if pos:
            pyautogui.click(pyautogui.center(pos))
            return True
        return False

    def _calc_relative_pos(self, ratio_pair):
        """根据比例系数计算实际坐标"""
        x = self.region[0] + int(self.region[2] * ratio_pair[0])
        y = self.region[1] + int(self.region[3] * ratio_pair[1])
        return (x, y)

    def set_time(self, hour, minute):
        """设置时间输入（相对坐标版）"""
        # 点击并输入小时
        hour_pos = self._calc_relative_pos(self.time_input_offsets['hour'])
        pyautogui.click(hour_pos)
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.write(f"{hour:02d}")

        # 点击并输入分钟
        minute_pos = self._calc_relative_pos(self.time_input_offsets['minute'])
        pyautogui.click(minute_pos)
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.write(f"{minute:02d}")

    def interactive_calibrate(self):
        """交互式坐标校准模式"""
        print("进入校准模式，请按提示操作：")
        # 校准小时输入框
        input("请手动点击小时输入框后按回车...")
        x, y = pyautogui.position()
        self.time_input_offsets['hour'] = (
            (x - self.region[0]) / self.region[2],
            (y - self.region[1]) / self.region[3]
        )
        # 校准分钟输入框
        input("请手动点击分钟输入框后按回车...")
        x, y = pyautogui.position()
        self.time_input_offsets['minute'] = (
            (x - self.region[0]) / self.region[2],
            (y - self.region[1]) / self.region[3]
        )
        print("校准完成！新参数：", self.time_input_offsets)

action = ""

#读取tmp.txt文件
with open('tmp.txt', 'r', encoding='utf-8') as f:
    action = f.read()

if __name__ == "__main__":
    try:
        # 启动闹钟应用
        pyautogui.hotkey('win', 's')
        time.sleep(0.5)

        pyperclip.copy("时钟")           # 中文复制到剪贴板
        pyautogui.hotkey('ctrl', 'v')   # 粘贴
        time.sleep(0.5)

        pyautogui.press('enter')
        time.sleep(1)  # 等待应用加载

        # 检测22:08:59格式的时间
        match3 = re.search(r'(\d{2}):(\d{2}):(\d{2})', action)
        if match3:
            hour, minute, second = map(int, match3.groups())
        # 检测22:08格式的时间
        match2 = re.search(r'(\d{2}):(\d{2})', action)

        
        if(match2 or match3):
            if match3:
                hour, minute, second = map(int, match3.groups())
            else:
                hour, minute = map(int, match2.groups())
                second = 0
            print(f"提取到的时间：{hour:02d}:{minute:02d}:{second:02d}")

            # 初始化控制器
            alarm = AlarmSetter("时钟")

            # 点击闹钟按钮
            if not alarm.click_in_window('extra/clock/001.png'):
                raise Exception("找不到闹钟按钮")
            time.sleep(1)

            # 点击添加按钮
            if not alarm.click_in_window('extra/clock/002.png'):
                raise Exception("找不到添加按钮")

            # 首次使用建议先校准
            # alarm.interactive_calibrate()

            # 设置时间
            alarm.set_time(hour, minute)
            print("时间设置成功")
            time.sleep(1)

            # 点击保存按钮
            save_pos = alarm._calc_relative_pos(alarm.time_input_offsets['save'])
            pyautogui.click(save_pos)
            print("闹钟设置成功")
        else:
            raise ValueError("未找到有效的时间格式")
        
    except Exception as e:
        print(f"错误发生: {e}")