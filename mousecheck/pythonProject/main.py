import cv2
import numpy as np
from mss import mss
from pynput.mouse import Listener as MouseListener
from pynput.keyboard import Listener as KeyboardListener, Key
from screeninfo import get_monitors
from neuracle_lib.triggerBox import TriggerIn
import os
import datetime

# 全局变量用于存储点击位置和状态
last_click_x = 0
last_click_y = 0
recording = False

triggerin = TriggerIn("COM3")
flag = triggerin.validate_device()
if not flag:
    raise Exception("Invalid Serial!")

# 创建以当前时间命名的文件夹
timestamp_folder = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
output_folder = os.path.join("screenshots", timestamp_folder)
os.makedirs(output_folder, exist_ok=True)

def save_screenshot(frame, x, y, monitor):
    # 在截图上标记点击位置
    if x is not None and y is not None:
        cv2.circle(frame, (x - monitor.x, y - monitor.y), 10, (0, 255, 0), -1)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S%f")
    filename = os.path.join(output_folder, f"screenshot_{timestamp}.png")
    cv2.imwrite(filename, frame)
    print(f"Screenshot saved: {filename}")

def on_click(x, y, button, pressed):
    global last_click_x, last_click_y, recording
    if pressed and recording:
        last_click_x, last_click_y = x, y
        try:
            triggerin.output_event_data(1)
            print("Trigger sent to EEG device.")
        except Exception as e:
            print(f"Error sending trigger: {e}")
        # Capture the current screen and save it
        sct = mss()
        monitor_region = {"top": selected_monitor.y, "left": selected_monitor.x, "width": selected_monitor.width, "height": selected_monitor.height}
        screen = np.array(sct.grab(monitor_region))
        frame = cv2.cvtColor(screen, cv2.COLOR_BGRA2BGR)
        save_screenshot(frame, last_click_x, last_click_y, selected_monitor)

def on_press(key):
    global recording
    if key == Key.space:
        recording = True
        print("Recording started.")
        return False  # Stop the keyboard listener

def capture_screen(monitor):
    global last_click_x, last_click_y
    sct = mss()
    monitor_region = {"top": monitor.y, "left": monitor.x, "width": monitor.width, "height": monitor.height}

    while True:
        screen = np.array(sct.grab(monitor_region))
        frame = cv2.cvtColor(screen, cv2.COLOR_BGRA2BGR)

        if last_click_x and last_click_y:
            cv2.circle(frame, (last_click_x - monitor.x, last_click_y - monitor.y), 10, (0, 255, 0), -1)

        cv2.namedWindow('Screen Capture', cv2.WINDOW_NORMAL)
        cv2.moveWindow('Screen Capture', 0, 0)
        cv2.resizeWindow('Screen Capture', 640, 480)
        cv2.imshow('Screen Capture', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break

monitors = get_monitors()
monitor_index = 1

if monitor_index >= len(monitors):
    raise Exception("Monitor index out of range. Available monitors: " + str(len(monitors)))

selected_monitor = monitors[monitor_index]

# 设置键盘监听
print("Press the space bar to start recording mouse clicks.")
with KeyboardListener(on_press=on_press) as keyboard_listener:
    keyboard_listener.join()

# 设置鼠标监听
mouse_listener = MouseListener(on_click=on_click)
mouse_listener.start()

# 开始屏幕捕获
capture_screen(selected_monitor)
