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

    runes, stat, hp, death, dmg_reward, find_reward, time_since_seen_boss, _ = rewardGen.update(frame)
    print("Runes:", runes)
    print("Stat:", stat)
    print("HP:", hp)
    print("dead:", death)
    print('dmg_reward', dmg_reward)
    print('find_reward', find_reward)
    print(rewardGen.current_stats)
    print(rewardGen.seen_boss)
    
    t_check_frozen_start = time.time()
    t_since_seen_next = None
    num_next = 0
    while True:
        frame = grab_screen_shot(sct)
        next_text_image = frame[1015:1040, 155:205]
        next_text_image = cv2.resize(next_text_image, ((205-155)*3, (1040-1015)*3))
        next_text = pytesseract.image_to_string(next_text_image,  lang='eng',config='--psm 6 --oem 3')

        lower = np.array([0,0,75])
        upper = np.array([255,255,255])
        hsv = cv2.cvtColor(next_text_image, cv2.COLOR_RGB2HSV)
        mask = cv2.inRange(hsv, lower, upper)
        matches = np.argwhere(mask==255)
        percent_match = len(matches) / (mask.shape[0] * mask.shape[1])
        next_text = pytesseract.image_to_string(mask,  lang='eng',config='--psm 6 --oem 3')
        loading_screen = "Next" in next_text or "next" in next_text
        if loading_screen or abs(percent_match - 0.195) < 0.02:
            t_since_seen_next = time.time()
            num_next += 1
        print(num_next)
        print(percent_match)
        cv2.imshow('demo', mask)
        cv2.waitKey(1)
    print(f"FPS: {1 / (time.time() - t0)}")
    