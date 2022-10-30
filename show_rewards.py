import cv2
from EldenReward import EldenReward
import time
import numpy as np
import pytesseract

cap = cv2.VideoCapture('/dev/video0')
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)


rewardGen = EldenReward(1, "templogs")

while True:
    ret, frame = cap.read()
    if not ret:
        break

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
    cv2.imshow('data', mask)
    cv2.waitKey(1)
            
    #cv2.waitKey(1)