import sys
import os
import threading
from threading import Thread
import torch
import cv2
from torch.cuda import device
from ultralytics import YOLO
import SystemEvent

lock = threading.Lock()

ai_dir = os.path.dirname(os.path.abspath(__file__))
file_out_dir = ai_dir + '/output/'
cam_list = ai_dir + '/cam_list.txt'

classes = [1, 2, 3, 5, 7]
device = '0'
conf = 0.2
if torch.backends.mps.is_available():
    device = 'mps'
elif torch.cuda.is_available():
    device = 'cuda:0'

def cam_to_source(cam):
    if not os.path.isfile(cam_list):
        print('main.py: cam_list file not found')
        return ''
    with open(cam_list, 'r') as file:
        for line in file:
            args = line.split()
            if len(args) != 2:
                print("main.py: cam_list format error")
                return ''
            if args[0] == cam:
                return 'http://admin:abcd123456789@' + args[1] + '/Streaming/channels/1/picture'
        print('main.py: ' + cam +' not specified in cam_list')
        return ''
    return ''


def predict(cam, file_out, classes = [], conf = conf, device = device):
    source = cam_to_source(cam)
    source = ai_dir + '/c.jpeg'
    if source == '':
        print('main.py: ' + cam + ' source not found')
    model = YOLO(ai_dir + "/models/yolo11x.pt")
    counter = dict()
    predictions = model.predict(source = source, classes = classes, conf = conf, device = device)
    for result in predictions:
        for box in result.boxes:
            cls = int(box.cls[0])
            class_name = model.names[cls]
            if class_name not in counter:
                counter[class_name] = 0
            counter[class_name] += 1
    with lock:
        file_out_path = file_out_dir + file_out
        os.makedirs(os.path.dirname(file_out_path), exist_ok=True)
        with open(file_out_path, 'w') as file:
            for key in counter:
                print(key, counter[key], file=file)


def main():
    while True:
        invocation = SystemEvent.SystemEvent('invoke')
        invocation.wait()
        invocation.clear()
        for i in range(1, 9):
            cam = 'cam' + str(i)
            agent = 'agent' + str(i)
            event_cam = SystemEvent.SystemEvent(cam)
            event_agent = SystemEvent.SystemEvent(agent)
            if event_cam.isSet():
                Thread(target=predict, args=(cam, cam + '.txt', classes, conf)).start()
                event_cam.clear()
                event_agent.set()

if __name__ == "__main__":
    main()
