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
    print(rewardGen.boss_hp)
    

    parry_image = frame[675:710, 85:150]
    parry_image = cv2.resize(parry_image, (parry_image.shape[1]*5, parry_image.shape[0]*5))
    parry_text = pytesseract.image_to_string(parry_image,  lang='eng',config='--psm 6 --oem 3')
    print(parry_text)

    cv2.imshow('data', parry_image)
    cv2.waitKey(1)
            
    #cv2.waitKey(1)