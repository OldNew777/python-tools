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
# 基础间隔时间（秒）
BASE_INTERVAL = 22.0
# 随机延时范围（秒）- 推荐这个范围更贴近人工操作，不易被检测
MIN_RANDOM_DELAY = 0.4
MAX_RANDOM_DELAY = 2.2
# 随机连击次数（1~2次）
MIN_CLICK_TIMES = 1
MAX_CLICK_TIMES = 2
# 连击之间的间隔（仿人手连续按的间隔）
MIN_CLICK_INTERVAL = 0.15
MAX_CLICK_INTERVAL = 0.35
# ================================================

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

def press_1():
    """模拟按下并松开 1 仿人工操作顺序）"""
    if not is_target_app_active():
        print("[提示] 当前前台不是燕云十六声，跳过本次按键")
        return
    
    try:
        # 随机生成本次连击次数（1或2次）
        click_times = random.randint(MIN_CLICK_TIMES, MAX_CLICK_TIMES)
        print(f"[执行] 准备连续按 1 键 {click_times} 次")
        
        for i in range(click_times):
            # 每次按键前的随机小延时（仿人手抬手/落手的间隔）
            if i > 0:  # 非第一次按键时，增加连击间隔
                interval = random.uniform(MIN_CLICK_INTERVAL, MAX_CLICK_INTERVAL)
                time.sleep(interval)
                print(f"[间隔] 第{i+1}次按键前等待 {interval:.2f} 秒")
            
            # 仿人手按下1键的完整动作
            time.sleep(random.uniform(0.05, 0.12))  # 按下前的微小延时
            keyboard_controller.press('1')          # 按下1键
            hold_time = random.uniform(0.08, 0.15)  # 按键保持时间
            time.sleep(hold_time)
            keyboard_controller.release('1')        # 松开1键
            print(f"[执行] 第{i+1}次按下 1 键（保持 {hold_time:.2f} 秒）")
            
    except Exception as e:
        print(f"[错误] 按键执行失败: {e}")

def macro_loop():
    """宏的循环执行逻辑"""
    global macro_running
    while macro_running:
        # 分段sleep，每0.5秒检查一次状态，方便快速退出
        remaining = BASE_INTERVAL
        while remaining > 0 and macro_running:
            time.sleep(0.5)
            remaining -= 0.5
        
        if not macro_running:
            break
        
        random_delay = random.uniform(MIN_RANDOM_DELAY, MAX_RANDOM_DELAY)
        # 同样分段sleep，支持快速响应退出
        delay_remaining = random_delay
        while delay_remaining > 0 and macro_running:
            time.sleep(0.5)
            delay_remaining -= 0.5
        
        if not macro_running:
            break
        
        press_1()

def toggle_macro():
    """切换宏的开启/关闭状态"""
    global macro_running, macro_thread
    
    macro_running = not macro_running
    if macro_running:
        print("\n=== 宏已开启 ===")
        press_1()
        # 启动新线程运行宏循环（避免阻塞键盘监听）
        macro_thread = threading.Thread(target=macro_loop, daemon=True)
        macro_thread.start()
    else:
        print("\n=== 宏已关闭 ===")
        # 等待线程自然结束（通过macro_running标志控制）
        if macro_thread is not None:
            macro_thread.join(timeout=1)

def on_key_press(key):
    """监听键盘按键，处理宏开关"""
    try:
        # 检测等号键按下（处理字符键的两种情况）
        if hasattr(key, 'char') and key.char == TOGGLE_KEY:
            toggle_macro()
    except AttributeError:
        # 忽略特殊按键的异常
        pass
    
def cleanup_and_exit(signal_num, frame):
    """处理退出信号，清理资源"""
    global macro_running, listener
    print("\n\n=== 正在退出程序 ===")
    # 停止宏运行
    macro_running = False
    # 停止键盘监听器
    if listener is not None and listener.is_alive():
        listener.stop()
    # 等待线程结束
    if macro_thread is not None and macro_thread.is_alive():
        macro_thread.join(timeout=2)
    print("=== 程序已安全退出 ===")
    exit(0)

def main():
    """主函数"""
    global listener
    print("=== 燕云十六声自动按键宏 ===")
    print(f"配置信息：")
    print(f"- 目标窗口：{TARGET_WINDOW_TITLE}")
    print(f"- 开关按键：{TOGGLE_KEY}（等号键）")
    print(f"- 基础间隔：{BASE_INTERVAL} 秒")
    print(f"- 随机延时：{MIN_RANDOM_DELAY}~{MAX_RANDOM_DELAY} 秒")
    print(f"- 执行按键：alt + 1")
    print("============================")
    print("按 = 键开启/关闭宏，按 Ctrl+C 退出程序\n")
    
    # 注册信号处理：捕获Ctrl+C（SIGINT）和终止信号（SIGTERM）
    signal.signal(signal.SIGINT, cleanup_and_exit)
    signal.signal(signal.SIGTERM, cleanup_and_exit)
    
    # 启动键盘监听器（非阻塞模式）
    listener = keyboard.Listener(on_press=on_key_press)
    listener.start()
    
    # 主线程循环，等待退出信号
    while listener.is_alive():
        time.sleep(0.1)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"程序出错: {e}")
