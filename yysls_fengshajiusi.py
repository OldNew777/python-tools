import time
import random
import threading
import ctypes
import signal
from pynput import keyboard
from pynput.keyboard import Controller, Key
import yysls_common


# ==================== 配置项 ====================
# 所有步骤通用的随机延时范围（秒）- 仿人工操作的随机波动
yysls_common.MIN_RANDOM_DELAY = 0.4
yysls_common.MAX_RANDOM_DELAY = 2.2
# 序列执行完成后，下一次序列开始的基础间隔时间（秒）
yysls_common.BASE_INTERVAL = 15

# ---------------- 各步骤固定等待时间（TODO：请替换为你需要的数值） ----------------
# 步骤1：初始等待（长按W前的等待）固定值
STEP1_INIT_WAIT_FIXED = 0.1  # TODO: 填写长按W前的固定等待秒数，如 1.5
# 步骤2：长按W的时长固定值
STEP2_HOLD_W_FIXED = 1     # TODO: 填写长按W的固定秒数，如 3.0
# 步骤3：长按W后 → 按F前的等待固定值
STEP3_W_TO_F_WAIT_FIXED = 0.5  # TODO: 填写固定秒数，如 0.8
# 步骤4：按F后 → 按N前的等待固定值
STEP4_F_TO_N_WAIT_FIXED = 15  # TODO: 填写固定秒数，如 0.5
# 步骤5：按N后 → 按Y前的等待固定值
STEP5_N_TO_Y_WAIT_FIXED = 15  # TODO: 填写固定秒数，如 0.5
# 步骤6：按Y后 → 按N前的等待固定值
STEP6_Y_TO_N_WAIT_FIXED = 15  # TODO: 填写固定秒数，如 0.5
# 步骤7：按N后 → 按N前的等待固定值
STEP7_N_TO_N_WAIT_FIXED = 15  # TODO: 填写固定秒数，如 0.5
# 步骤8：按N后 → 按Y前的等待固定值
STEP8_N_TO_Y_WAIT_FIXED = 15  # TODO: 填写固定秒数，如 0.5
# 步骤9：按Y后 → 按F前的等待固定值
STEP9_Y_TO_F_WAIT_FIXED = 30  # TODO: 填写固定秒数，如 0.8
# ================================================


def run_key_sequence():
    """执行完整的按键序列：初始等待→长按W→按F→按N→按Y→按N→按N→按Y→按F"""
    if not yysls_common.is_target_app_active():
        print("[提示] 当前前台不是燕云十六声，跳过本次序列执行")
        return
    
    try:
        print("\n=====================================")
        print("[开始] 执行按键序列")
        print("=====================================")
        
        # 步骤1：初始等待（长按W前）
        step1_wait, step1_rand = yysls_common.get_wait_time(STEP1_INIT_WAIT_FIXED)
        print(f"[步骤1] 初始等待 {step1_wait:.2f} 秒（固定{STEP1_INIT_WAIT_FIXED} + 随机{step1_rand:.2f}）")
        # 分段sleep，支持快速退出
        if not yysls_common.sync_wait_for(step1_wait):
            return
        
        # 步骤2：长按W键
        step2_hold, step2_rand = yysls_common.get_wait_time(STEP2_HOLD_W_FIXED)
        print(f"[步骤2] 长按W键 {step2_hold:.2f} 秒（固定{STEP2_HOLD_W_FIXED} + 随机{step2_rand:.2f}）")
        yysls_common.keyboard_controller.press('w')
        # 分段sleep，支持快速退出
        yysls_common.sync_wait_for(step2_hold)
        if yysls_common.macro_running:
            yysls_common.keyboard_controller.release('w')
            print("[步骤2] 松开W键")
        else:
            yysls_common.keyboard_controller.release('w')
            return
        
        # 步骤3：长按W后 → 按F前的等待
        step3_wait, step3_rand = yysls_common.get_wait_time(STEP3_W_TO_F_WAIT_FIXED)
        print(f"[步骤3] 等待 {step3_wait:.2f} 秒（固定{STEP3_W_TO_F_WAIT_FIXED} + 随机{step3_rand:.2f}）")
        if not yysls_common.sync_wait_for(step3_wait):
            return
        
        # 步骤4：按F键（仿人手操作）
        print("[步骤4] 按F键")
        time.sleep(random.uniform(0.05, 0.12))  # 按下前微小延时
        yysls_common.keyboard_controller.press('f')
        hold_f = random.uniform(0.08, 0.15)
        time.sleep(hold_f)
        yysls_common.keyboard_controller.release('f')
        print(f"[步骤4] 松开F键（保持{hold_f:.2f}秒）")
        if not yysls_common.macro_running:
            return
        
        # 步骤5：按F后 → 按N前的等待
        step5_wait, step5_rand = yysls_common.get_wait_time(STEP4_F_TO_N_WAIT_FIXED)
        print(f"[步骤5] 等待 {step5_wait:.2f} 秒（固定{STEP4_F_TO_N_WAIT_FIXED} + 随机{step5_rand:.2f}）")
        if not yysls_common.sync_wait_for(step5_wait):
            return
        
        # 步骤6：按N键
        print("[步骤6] 按N键")
        time.sleep(random.uniform(0.05, 0.12))
        yysls_common.keyboard_controller.press('n')
        hold_n1 = random.uniform(0.08, 0.15)
        time.sleep(hold_n1)
        yysls_common.keyboard_controller.release('n')
        print(f"[步骤6] 松开N键（保持{hold_n1:.2f}秒）")
        if not yysls_common.macro_running:
            return
        
        # 步骤7：按N后 → 按Y前的等待
        step7_wait, step7_rand = yysls_common.get_wait_time(STEP5_N_TO_Y_WAIT_FIXED)
        print(f"[步骤7] 等待 {step7_wait:.2f} 秒（固定{STEP5_N_TO_Y_WAIT_FIXED} + 随机{step7_rand:.2f}）")
        if not yysls_common.sync_wait_for(step7_wait):
            return
        
        # 步骤8：按Y键
        print("[步骤8] 按Y键")
        time.sleep(random.uniform(0.05, 0.12))
        yysls_common.keyboard_controller.press('y')
        hold_y1 = random.uniform(0.08, 0.15)
        time.sleep(hold_y1)
        yysls_common.keyboard_controller.release('y')
        print(f"[步骤8] 松开Y键（保持{hold_y1:.2f}秒）")
        if not yysls_common.macro_running:
            return
        
        # 步骤9：按Y后 → 按N前的等待
        step9_wait, step9_rand = yysls_common.get_wait_time(STEP6_Y_TO_N_WAIT_FIXED)
        print(f"[步骤9] 等待 {step9_wait:.2f} 秒（固定{STEP6_Y_TO_N_WAIT_FIXED} + 随机{step9_rand:.2f}）")
        if not yysls_common.sync_wait_for(step9_wait):
            return
        
        # 步骤10：按N键
        print("[步骤10] 按N键")
        time.sleep(random.uniform(0.05, 0.12))
        yysls_common.keyboard_controller.press('n')
        hold_n2 = random.uniform(0.08, 0.15)
        time.sleep(hold_n2)
        yysls_common.keyboard_controller.release('n')
        print(f"[步骤10] 松开N键（保持{hold_n2:.2f}秒）")
        if not yysls_common.macro_running:
            return
        
        # 步骤11：按N后 → 按N前的等待
        step11_wait, step11_rand = yysls_common.get_wait_time(STEP7_N_TO_N_WAIT_FIXED)
        print(f"[步骤11] 等待 {step11_wait:.2f} 秒（固定{STEP7_N_TO_N_WAIT_FIXED} + 随机{step11_rand:.2f}）")
        if not yysls_common.sync_wait_for(step11_wait):
            return
        
        # 步骤12：按N键
        print("[步骤12] 按N键")
        time.sleep(random.uniform(0.05, 0.12))
        yysls_common.keyboard_controller.press('n')
        hold_n3 = random.uniform(0.08, 0.15)
        time.sleep(hold_n3)
        yysls_common.keyboard_controller.release('n')
        print(f"[步骤12] 松开N键（保持{hold_n3:.2f}秒）")
        if not yysls_common.macro_running:
            return
        
        # 步骤13：按N后 → 按Y前的等待
        step13_wait, step13_rand = yysls_common.get_wait_time(STEP8_N_TO_Y_WAIT_FIXED)
        print(f"[步骤13] 等待 {step13_wait:.2f} 秒（固定{STEP8_N_TO_Y_WAIT_FIXED} + 随机{step13_rand:.2f}）")
        if not yysls_common.sync_wait_for(step13_wait):
            return
        
        # 步骤14：按Y键
        print("[步骤14] 按Y键")
        time.sleep(random.uniform(0.05, 0.12))
        yysls_common.keyboard_controller.press('y')
        hold_y2 = random.uniform(0.08, 0.15)
        time.sleep(hold_y2)
        yysls_common.keyboard_controller.release('y')
        print(f"[步骤14] 松开Y键（保持{hold_y2:.2f}秒）")
        if not yysls_common.macro_running:
            return
        
        # 步骤15：按Y后 → 按F前的等待
        step15_wait, step15_rand = yysls_common.get_wait_time(STEP9_Y_TO_F_WAIT_FIXED)
        print(f"[步骤15] 等待 {step15_wait:.2f} 秒（固定{STEP9_Y_TO_F_WAIT_FIXED} + 随机{step15_rand:.2f}）")
        if not yysls_common.sync_wait_for(step15_wait):
            return
        
        # 步骤16：按F键
        print("[步骤16] 按F键")
        time.sleep(random.uniform(0.05, 0.12))
        yysls_common.keyboard_controller.press('f')
        hold_f2 = random.uniform(0.08, 0.15)
        time.sleep(hold_f2)
        yysls_common.keyboard_controller.release('f')
        print(f"[步骤16] 松开F键（保持{hold_f2:.2f}秒）")
        
        print("=====================================")
        print("[完成] 本次按键序列执行完毕")
        print("=====================================")
        
    except ValueError as ve:
        print(f"[错误] 配置项未填写完整：{ve}")
    except Exception as e:
        print(f"[错误] 序列执行失败: {e}")
        # 异常时确保所有按键松开，避免卡键
        yysls_common.keyboard_controller.release('w')
        yysls_common.keyboard_controller.release('f')
        yysls_common.keyboard_controller.release('n')
        yysls_common.keyboard_controller.release('y')

def macro_loop():
    """宏的循环执行逻辑"""
    while yysls_common.macro_running:
        # 执行完整按键序列
        run_key_sequence()
        
        if not yysls_common.macro_running:
            break
        
        # 序列执行完后，等待基础间隔+随机延时，再开始下一次
        interval_wait, interval_rand = yysls_common.get_wait_time(yysls_common.BASE_INTERVAL)
        print(f"[等待] 下一次序列执行前，等待 {interval_wait:.2f} 秒（固定{STEP9_Y_TO_F_WAIT_FIXED} + 随机{interval_rand:.2f}）")
        # 分段sleep，支持快速退出
        if not yysls_common.sync_wait_for(interval_wait):
            return

def toggle_macro():
    """切换宏的开启/关闭状态"""
    yysls_common.macro_running = not yysls_common.macro_running
    if yysls_common.macro_running:
        print("\n=== 宏已开启 ===")
        # 启动新线程运行宏循环（避免阻塞键盘监听）
        yysls_common.macro_thread = threading.Thread(target=macro_loop, daemon=True)
        yysls_common.macro_thread.start()
    else:
        print("\n=== 宏已关闭 ===")
        # 等待线程自然结束
        if yysls_common.macro_thread is not None:
            yysls_common.macro_thread.join(timeout=1)

def on_key_press(key):
    """监听键盘按键，处理宏开关"""
    try:
        # 检测等号键按下
        if hasattr(key, 'char') and key.char == yysls_common.TOGGLE_KEY:
            toggle_macro()
    except AttributeError:
        # 忽略特殊按键的异常
        pass

def cleanup_and_exit(signal_num, frame):
    """处理退出信号，清理资源"""
    print("\n\n=== 正在退出程序 ===")
    # 停止宏运行
    yysls_common.macro_running = False
    # 确保所有按键松开
    yysls_common.keyboard_controller.release('w')
    yysls_common.keyboard_controller.release('f')
    yysls_common.keyboard_controller.release('n')
    yysls_common.keyboard_controller.release('y')
    # 停止键盘监听器
    if yysls_common.listener is not None and yysls_common.listener.is_alive():
        yysls_common.listener.stop()
    # 等待线程结束
    if yysls_common.macro_thread is not None and yysls_common.macro_thread.is_alive():
        yysls_common.macro_thread.join(timeout=2)
    print("=== 程序已安全退出 ===")
    exit(0)

def main():
    """主函数"""
    print("=== 燕云十六声序列按键宏 ===")
    print(f"配置信息：")
    print(f"- 目标窗口：{yysls_common.TARGET_WINDOW_TITLE}")
    print(f"- 开关按键：{yysls_common.TOGGLE_KEY}（等号键）")
    print(f"- 序列间隔：{yysls_common.BASE_INTERVAL} 秒 + 随机{yysls_common.MIN_RANDOM_DELAY}~{yysls_common.MAX_RANDOM_DELAY}秒")
    print(f"- 序列内容：初始等待→长按W→按F→按N→按Y→按N→按N→按Y→按F")
    print("============================")
    print("⚠️  请先在配置项中填写所有TODO的固定等待时间！")
    print("按 = 键开启/关闭宏，按 Ctrl+C 退出程序\n")
    
    # 注册信号处理：捕获Ctrl+C
    signal.signal(signal.SIGINT, cleanup_and_exit)
    signal.signal(signal.SIGTERM, cleanup_and_exit)
    
    # 启动键盘监听器（非阻塞模式）
    yysls_common.listener = keyboard.Listener(on_press=on_key_press)
    yysls_common.listener.start()
    
    # 主线程循环，等待退出信号
    while yysls_common.listener.is_alive():
        time.sleep(0.1)

if __name__ == "__main__":
    # 首次运行请安装依赖：pip install pynput
    try:
        main()
    except Exception as e:
        print(f"程序出错: {e}")
