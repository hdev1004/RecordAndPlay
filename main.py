from pynput import keyboard
from pynput.keyboard import Controller, Key
import time
import keyboard as kb
import threading
import keyMapping
import json
import os
import pyautogui
from ctypes import *
import signal


DD = windll.LoadLibrary('dlls/dd32695.x64.dll')
print("Load DD!")
st = DD.DD_btn(0) #DD Initialize
if st==1:
    print("OK")
else:
    print("Error")
    exit(101)


# 고려사항
# 1. 키가 계속 눌려져 있는가?
# 2. Ctrl 조합키를 고려 했는가?

isRecord = False
beforeInputKey = None
recoding_number = 0
recoding = {}

def save_dict_to_file(my_dict, base_filename='recoding'):
    # 기본 파일 이름에 번호를 붙여가며 중복을 피함
    filename = f"{base_filename}.json"
    count = 1

    while os.path.exists(filename):
        filename = f"{base_filename}_{count}.json"
        count += 1

    # 딕셔너리를 JSON 형식으로 변환하여 파일에 쓰기
    with open(filename, 'w') as json_file:
        json.dump(my_dict, json_file)

    print(f"Dictionary saved to file: {filename}")

def on_press(key):
    global beforeInputKey
    global isRecord
    global recoding_number
    ctrl_mapping = keyMapping.ctrl_mapping

    # 종료 조건
    if key == keyboard.Key.esc:
        #파일로 저장
        if isRecord == True: #녹화중이였다면
            save_dict_to_file(recoding)
            isRecord = False
        return False

    if isRecord == True:
        try:
            #1. 키가 계속 눌려져 있을경우 처리
            cur_key_code = key

            #2. Ctrl 조합키를 고려
            if key in ctrl_mapping:
                cur_key_code = ctrl_mapping[key]
            if cur_key_code == "<21>": #한글키 변경
                cur_key_code = "hangul"

            recoding[recoding_number] = {
                "key":  str(cur_key_code) if type(cur_key_code) is Key else cur_key_code.char,
                "time": time.time(),
                "type": "press"
            }
            recoding_number += 1

        except AttributeError:
            print("Special Key Press : {0}".format(key))


    # 실행 조건
    if key == keyboard.Key.f1:
        if isRecord == False:
            recoding["start_time"] = time.time()
            print("keyboard recording start")
            isRecord = True


def on_release(key):
    global isRecord
    global recoding_number
    ctrl_mapping = keyMapping.ctrl_mapping

    if isRecord == True and key != Key.f1:
        cur_key_code = key
        if key in ctrl_mapping:
            cur_key_code = ctrl_mapping[key]

        recoding[recoding_number] = {
            "key":  str(cur_key_code) if type(cur_key_code) is Key else cur_key_code.char,
            "time": time.time(),
            "type": "release"
        }

        recoding_number += 1


# 녹화할 때
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
####



# ====== 시작 =====



from pynput import keyboard
from pynput.keyboard import Controller, Key
import time
import keyboard as kb
import threading
import keyMapping
import json
import os
import pyautogui
from ctypes import *
import signal


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
        print("delay : " + str(delay) + "," + "key : " + self.key)
        classDD_mapping = keyMapping.classDD_mapping
        time.sleep(delay)

        try:
            input_key = self.key
            #if input_key in key_mapping:
            #    input_key = key_mapping[self.key]

            if input_key in classDD_mapping: #다시한번 매핑(임시 테스트용)
               input_key = classDD_mapping[self.key]
               print("name : ", self.name)
               print("TRANSE INPUT : ", input_key)

            #input_key = input_key.lower()

            if self.type == "press":
                #pyautogui.keyDown(input_key)
                DD.DD_key(input_key, 1)
            else:
                #pyautogui.keyUp(input_key)
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
    # Your on_press_play logic here
    if key == keyboard.Key.esc:
        # 파일로 저장
       kill_process()

def on_release_play(key):
    # Your on_release_play logic here
    return

def start_listener():
    with keyboard.Listener(on_press=on_press_play, on_release=on_release_play) as listener:
        listener.join()

listener_thread = threading.Thread(target=start_listener)
listener_thread.daemon = True
listener_thread.start()

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


while True:
    for key in json_data:
        if key == "start_time":
            continue
        name = "thread {}".format(key)
        t = Worker(start_time, name, json_data[key]["key"], json_data[key]["time"], json_data[key]["type"])  # sub thread 생성
        t.start()
    time.sleep(end_time)

