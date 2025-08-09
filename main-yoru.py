import asyncio
import datetime
import json
import os
import time

import cv2
import schedule
from ultralytics import YOLO


def load_yolo_model(model_path='./assets/yolov8s.pt'):
    model = YOLO(model_path)
    return model

def load_config_people_settings():
    with open("./data/room_status.json", encoding="utf-8") as f:
        data = json.load(f)
    return data


people_settings = load_config_people_settings()
model = load_yolo_model()
print(f"モデルがロードされました: {model}")


def detect_video(m):
    date_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open("./data/room_status.json", encoding="utf-8") as f:
        data = json.load(f)

    cap = cv2.VideoCapture(os.getenv("VIDEO_PATH"))

    ret, frame = cap.read()
    if not ret:
        print(f"[{date_now}] no ret")
    else:
        try:
            results = m(frame)
            people_count = 0
            for r in results:
                boxes = r.boxes
                for box in boxes:
                    if box.cls[0] == 0:
                        people_count += 1
                        x1, y1, x2, y2 = box.xyxy[0]
                        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)

            if people_count < people_settings.get("quietCount"):
                data["roomStatus"] = 0
            elif people_count < people_settings.get("slightlyCrowdedCount"):
                data["roomStatus"] = 1
            elif people_count < people_settings.get("crowdedCount"):
                data["roomStatus"] = 2
            elif people_count < people_settings.get("hugeCrowdedCount"):
                data["roomStatus"] = 3
            else:
                data["roomStatus"] = 4

            with open("./data/room_count.json", "w", encoding="utf-8") as f:
                data["peopleCount"] = people_count
                json.dump(data, f, ensure_ascii=False, indent=4)

            print(f"[{date_now}] 人数: {people_count}")
        except Exception as e:
            print(f"[{date_now}] エラー：{e}")


async def loop_detect_video():
    schedule.every(1).minutes.do(detect_video, m=model)
    while True:
        schedule.run_pending()
        time.sleep(1)

asyncio.run(loop_detect_video())
