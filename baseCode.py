from pynput import keyboard

# 기록된 키 이벤트를 저장할 리스트
recorded_events = []

# 키를 누를 때 호출되는 콜백 함수
def on_press(key):
    try:
        # 키보드 입력을 문자열로 변환하여 리스트에 추가
        recorded_events.append(str(key.char))
    except AttributeError:
        # 특수 키의 경우, 그냥 문자열로 추가
        recorded_events.append(str(key))

# 키를 떼었을 때 호출되는 콜백 함수
def on_release(key):
    if key == keyboard.Key.esc:
        # 'esc' 키를 누르면 녹화 종료
        return False

# 키보드 리스너 생성
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    # 리스너가 실행되는 동안 대기
    listener.join()

# 녹화된 키 이벤트 출력
print("Recorded Events:")
print(recorded_events)