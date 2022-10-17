import cv2
from EldenReward import EldenReward
import time
import numpy as np

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
    hp_image = frame[45:55, 155:155 + int(rewardGen.max_hp * rewardGen.hp_ratio)]
    end_leng = 155 + int(rewardGen.max_hp * rewardGen.hp_ratio)
    p_count = 0
    for i in range(int(rewardGen.max_hp * rewardGen.hp_ratio)):
        avg = 0
        for j in range(10):
            r = np.float64(hp_image[j, i][0])
            g = np.float64(hp_image[j, i][1])
            b = np.float64(hp_image[j, i][2])
            avg = np.float64((r + g + b)) / 3
        print(avg)
        if avg > 100:
            p_count += 1
        if p_count > 5:
            print("HP:", i / int(rewardGen.max_hp * rewardGen.hp_ratio))
            break
    if p_count < 5:
        print("HP:", 0)
            
    
            
    #cv2.waitKey(1)