import cv2
from EldenReward import EldenReward
import time
import numpy as np
import pytesseract
import base64
import requests
from mss.linux import MSS as mss


rewardGen = EldenReward(1, "templogs")
sct = mss()


def grab_screen_shot(sct):
    for num, monitor in enumerate(sct.monitors[1:], 1):
        # Get raw pixels from the screen
        sct_img = sct.grab(monitor)

        # Create the Image
        #decoded = cv2.imdecode(np.frombuffer(sct_img, np.uint8), -1)
        return cv2.cvtColor(np.asarray(sct_img), cv2.COLOR_BGRA2RGB)


while True:
    t0 = time.time()
    frame = grab_screen_shot(sct)
    print(frame.shape)

    rewardGen.update(frame)
    
    t_check_frozen_start = time.time()
    t_since_seen_next = None
    num_next = 0
    while True:
        frame = grab_screen_shot(sct)
        lock_on_img = frame[:820, 470:1600]

        lock_on_img = frame[200:500, 700:1300]

        lower = np.array([100,0,150])
        upper = np.array([150,75,255])
        hsv = cv2.cvtColor(lock_on_img, cv2.COLOR_RGB2HSV)
        mask = cv2.inRange(hsv, lower, upper)
        matches = np.argwhere(mask==255)
        percent_match = len(matches)
        print(percent_match)
        cv2.imshow('demo', mask)
        cv2.waitKey(1)
    print(f"FPS: {1 / (time.time() - t0)}")
    