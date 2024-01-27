
from pynput import keyboard
import time
import threading
import keyMapping
import json
import os
from ctypes import *
import signal


# ClassDD 라이브러리 불러오기
DD = windll.LoadLibrary('dlls/dd32695.x64.dll')
print("Load DD!")
st = DD.DD_btn(0) #DD Initialize
if st==1:
    print("OK")
else:
    print("Error")
    exit(101)


class Worker(threading.Thread):
    def __init__(self, start_time, name, key, time, type):
        super().__init__()
        self.start_time = start_time
        self.name = name            # thread 이름 지정
        self.key = key
        self.time = time
        self.type = type

    def run(self):
        delay = round(max(0, self.time - self.start_time), 4)
        classDD_mapping = keyMapping.classDD_mapping
        time.sleep(delay)

        try:
            input_key = self.key
            # 키보드 라이브러리 사용
            #if input_key in key_mapping:
            #    input_key = key_mapping[self.key]

            # ClassDD 라이브러리 사용
            if input_key in classDD_mapping: #다시한번 매핑(임시 테스트용)
                #if len(input_key) == 1:
                #    input_key = input_key.lower()
                input_key = classDD_mapping[input_key]

            if self.type == "press":
                # 키보드 라이브러리 사용
                #pyautogui.keyDown(input_key)

                # ClassDD 라이브러리 사용
                DD.DD_key(input_key, 1)
            else:
                # 키보드 라이브러리 사용
                #pyautogui.keyUp(input_key)

                # ClassDD 라이브러리 사용
                DD.DD_key(input_key, 2)
        except Exception as ex:
            print("오류 : ", ex)
        return


def kill_process():
    # 현재 실행 중인 프로세스의 PID 얻기
    current_pid = os.getpid()
    print(current_pid)
    try:
        # SIGTERM 시그널을 사용하여 프로세스 종료 시도
        os.kill(current_pid, signal.SIGTERM)
        print(f"프로세스 {current_pid}를 종료하는 데 성공했습니다.")
    except OSError:
        print(f"프로세스 {current_pid}를 종료하는 데 실패했습니다.")

def on_press_play(key):
    if key == keyboard.Key.esc:
       kill_process()

def on_release_play(key):
    return

    # 종료 프로세스
def start_listener():
    with keyboard.Listener(on_press=on_press_play, on_release=on_release_play) as listener:
        listener.join()

# 키보드 리스너 실행
listener_thread = threading.Thread(target=start_listener)
listener_thread.daemon = True
listener_thread.start()


# 2초뒤 실행
print("Ready")
time.sleep(2)
print("Start")
with open("recoding.json", 'r') as f:
    json_data = json.load(f)

start_time = json_data["start_time"]
last_number = str(max(list(map(int, list(json_data.keys())[1:]))))
last_time = json_data[last_number]["time"]
end_time = round(last_time - start_time, 4) + 0.5 #혹시나 겹치는 상황을 대비

listener_thread = threading.Thread(target=start_listener)

for key in json_data:
    if key == "start_time":
        continue
    name = "thread {}".format(key)
    t = Worker(start_time, name, json_data[key]["key"], json_data[key]["time"], json_data[key]["type"])  # sub thread 생성
    t.start()

