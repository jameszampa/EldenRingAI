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

    runes, stat, hp, death, dmg_reward, find_reward, time_since_seen_boss = rewardGen.update(frame)
    print("Runes:", runes)
    print("Stat:", stat)
    print("HP:", hp)
    print("dead:", death)
    print('dmg_reward', dmg_reward)
    print('find_reward', find_reward)
    print(rewardGen.current_stats)
    print(rewardGen.seen_boss)
    
    
    boss_hp = 1
    boss_hp_image = frame[869:873, 475:1460]
    lower = np.array([0,0,75])
    upper = np.array([150,255,255])
    hsv = cv2.cvtColor(boss_hp_image, cv2.COLOR_RGB2HSV)
    mask = cv2.inRange(hsv, lower, upper)
    matches = np.argwhere(mask==255)
    boss_hp = len(matches) / (boss_hp_image.shape[1] * boss_hp_image.shape[0])
    print(boss_hp)
    # 
    cv2.imshow('data', mask)
    cv2.waitKey(1)
    print(f"FPS: {1 / (time.time() - t0)}")
    #cv2.waitKey(1)