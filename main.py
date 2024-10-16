import json
import os
import threading
from threading import Thread

import SystemEvent
import torch
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from torch.cuda import device
from ultralytics import YOLO

lock = threading.Lock()

ai_dir = os.path.dirname(os.path.abspath(__file__))
file_out_dir = ai_dir + "/output/"
json_file_name = ai_dir + "/config.json"

classes = [1, 2, 3, 5, 7]
conf = 0.2


if torch.backends.mps.is_available():
    device = "mps"
elif torch.cuda.is_available():
    device = "cuda:0"


def json_parse(target):
    source = ""
    zone = None
    with open(json_file_name) as json_file:
        json_obj = json.load(json_file)
        if target in json_obj:
            obj = json_obj[target]
            if obj["type"] == "cam":
                username = obj["username"]
                password = obj["password"]
                ip = obj["ip"]
                source = (
                    "http://"
                    + username
                    + ":"
                    + password
                    + "@"
                    + ip
                    + "/Streaming/channels/1/picture"
                )
                zone = obj["zone"]
            elif obj["type"] == "image":
                source = obj["path"]
                zone = obj["zone"]
    return source, zone


def predict(cam, classes=[], conf=conf, device="cpu"):
    source, zone = json_parse(cam)
    if source == "":
        print("main.py: " + cam + " source not found")
        return
    file_out = os.path.basename(source + ".txt")
    counter = dict()
    model = YOLO(ai_dir + "/models/yolo11x.pt")
    predictions = model.predict(
        source=source, classes=classes, conf=conf, device=device
    )
    for result in predictions:
        img_shape = result.orig_shape
        if zone is None:
            zone = [(0, 0), (0, img_shape[1]), img_shape, (img_shape[0], 0)]
        polygon = Polygon(zone)
        # result.show()
        for box in result.boxes:
            cls = int(box.cls[0])
            class_name = model.names[cls]
            if class_name not in counter:
                counter[class_name] = 0
            centroid = Point(
                (float(box.xyxyn[0][2]) + float(box.xyxyn[0][0])) / 2 * img_shape[0],
                (float(box.xyxyn[0][3]) + float(box.xyxyn[0][1])) / 2 * img_shape[1],
            )
            if polygon.contains(centroid):
                counter[class_name] += 1
    with lock:
        file_out_path = file_out_dir + file_out
        os.makedirs(os.path.dirname(file_out_path), exist_ok=True)
        with open(file_out_path, "w") as file:
            for key in counter:
                print(key, counter[key], file=file)


def main():
    while True:
        invocation = SystemEvent.SystemEvent("invoke")
        invocation.wait()
        invocation.clear()
        with open(json_file_name) as json_file:
            json_obj = json.load(json_file)
            for obj in json_obj:
                event_target = SystemEvent.SystemEvent(obj)
                event_agent = SystemEvent.SystemEvent("agent-" + obj)
                if event_target.isSet():
                    Thread(target=predict, args=(obj, classes, conf)).start()
                    event_target.clear()
                    event_agent.set()


if __name__ == "__main__":
    main()
