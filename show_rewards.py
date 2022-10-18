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
    lost_connection_image = frame[475:550, 675:1250]
    lost_connection_image = cv2.resize(lost_connection_image, ((1250-675)*3, (550-475)*3))
    lost_connection_text = pytesseract.image_to_string(lost_connection_image,  lang='eng',config='--psm 6 --oem 3')
    print(lost_connection_text)
    
            
    #cv2.waitKey(1)