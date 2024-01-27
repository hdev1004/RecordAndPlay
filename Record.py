from pynput import keyboard
from pynput.keyboard import Key
import time
import keyMapping
import json
import os

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
            #1. 키가 계속 눌려져 있을경우 처리 (처리 할필요 없음)
            cur_key_code = key

            #2. Ctrl 조합키를 고려
            if key in ctrl_mapping:
                cur_key_code = ctrl_mapping[key]
            if cur_key_code == "<21>": #한글키 변경
                cur_key_code = "hangul"

            recoding[recoding_number] = {
                "key":  str(cur_key_code) if type(cur_key_code) is Key else cur_key_code.char.lower(),
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
            "key":  str(cur_key_code) if type(cur_key_code) is Key else cur_key_code.char.lower(),
            "time": time.time(),
            "type": "release"
        }

        recoding_number += 1


# 녹화할 때
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    print("======= MENU =======")
    print("F1 : 녹화")
    print("ESC : 종료")
    print("======= MENU =======")
    listener.join()
####

