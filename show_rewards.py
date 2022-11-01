import cv2
from EldenReward import EldenReward
import time
import numpy as np
import pytesseract
import base64
import requests

rewardGen = EldenReward(1, "templogs")

while True:
    t0 = time.time()
    headers = {"Content-Type": "application/json"}
    response = requests.post(f"http://192.168.4.70:6000/action/focus_window", headers=headers)
    headers = {"Content-Type": "application/json"}
    response = requests.post(f"http://192.168.4.70:6000/action/screen_shot", headers=headers)

    #print(response.json())

    #frame = base64.decodebytes()
    frame = np.fromstring(response.json()['img'], np.uint8)
    frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    runes, stat, hp, death, dmg_reward, find_reward, time_since_seen_boss = rewardGen.update(frame)
    print("Runes:", runes)
    print("Stat:", stat)
    print("HP:", hp)
    print("dead:", death)
    print('dmg_reward', dmg_reward)
    print('find_reward', find_reward)
    print(rewardGen.current_stats)
    print(rewardGen.seen_boss)
    #print(rewardGen.boss_hp)
    

    hp_image = frame[51:55, 155:155 + int(rewardGen.max_hp * rewardGen.hp_ratio) - 20]
    lower = np.array([0,150,95])
    upper = np.array([150,255,125])
    #lower = np.array([0,0,150])
    #upper = np.array([255,255,255])
    hsv = cv2.cvtColor(hp_image, cv2.COLOR_RGB2HSV)
    mask = cv2.inRange(hsv, lower, upper)
    matches = np.argwhere(mask==255)
    print("PlayerHP:", len(matches) / (hp_image.shape[1] * hp_image.shape[0]))
    
    # 
    cv2.imshow('data', frame)
    cv2.waitKey(1)
    print(f"FPS: {1 / (time.time() - t0)}")
    #cv2.waitKey(1)