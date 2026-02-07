import time
import random
import threading
import ctypes
import signal
from pynput import keyboard
from pynput.keyboard import Controller, Key

# ==================== 配置项 ====================
# 目标窗口名称（支持模糊匹配）
TARGET_WINDOW_TITLE = "燕云十六声"

# 宏开关按键（等号键）
TOGGLE_KEY = '='
# 所有步骤通用的随机延时范围（秒）- 仿人工操作的随机波动
MIN_RANDOM_DELAY = 0.4
MAX_RANDOM_DELAY = 2.2
# 序列执行完成后，下一次序列开始的基础间隔时间（秒）
BASE_INTERVAL = 15

# 全局变量
keyboard_controller = Controller()
macro_running = False  # 宏运行状态
macro_thread = None    # 宏执行线程
listener = None        # 键盘监听器实例


def get_foreground_window_title():
    """获取前台活动窗口的标题"""
    try:
        user32 = ctypes.WinDLL('user32', use_last_error=True)
        hwnd = user32.GetForegroundWindow()
        length = user32.GetWindowTextLengthW(hwnd)
        if length == 0:
            return ""
        buffer = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buffer, length + 1)
        return buffer.value
    except Exception as e:
        print(f"获取窗口标题出错: {e}")
        return ""

def is_target_app_active():
    """检查前台窗口是否是燕云十六声"""
    window_title = get_foreground_window_title()
    return TARGET_WINDOW_TITLE in window_title

def get_wait_time(fixed_value):
    """计算等待时间 = 固定值 + 随机值（防检测）"""
    if fixed_value is None:
        raise ValueError("请先在配置项中填写所有TODO的固定等待时间！")
    random_offset = random.uniform(MIN_RANDOM_DELAY, MAX_RANDOM_DELAY)
    total_wait = fixed_value + random_offset
    return total_wait, random_offset

# def on_key_press(key):
#     """监听键盘按键，处理宏开关"""
#     try:
#         # 检测等号键按下（处理字符键的两种情况）
#         if hasattr(key, 'char') and key.char == TOGGLE_KEY:
#             toggle_macro()
#     except AttributeError:
#         # 忽略特殊按键的异常
#         pass
    
# def cleanup_and_exit(signal_num, frame):
#     """处理退出信号，清理资源"""
#     global macro_running, listener
#     print("\n\n=== 正在退出程序 ===")
#     # 停止宏运行
#     macro_running = False
#     # 停止键盘监听器
#     if listener is not None and listener.is_alive():
#         listener.stop()
#     # 等待线程结束
#     if macro_thread is not None and macro_thread.is_alive():
#         macro_thread.join(timeout=2)
#     print("=== 程序已安全退出 ===")
#     exit(0)


def sync_wait_for(time_seconds):
    global macro_running
    print(f'macro_running = {macro_running}')
    while time_seconds > 0 and macro_running:
        time.sleep(0.5)
        time_seconds -= 0.5
    if not macro_running:
        return False
    return True
    