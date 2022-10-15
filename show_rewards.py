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
    # cv2.imshow('er', )
    if rewardGen.seen_boss:
        hp_image = frame[865:875, 465:1460]
        p_count = 0
        for i in range(int(1460 - 465)):
            avg = 0
            for j in range(10):
                r = np.float64(hp_image[j, (1460 - 465 - 1) - i][0])
                g = np.float64(hp_image[j, (1460 - 465 - 1) - i][1])
                b = np.float64(hp_image[j, (1460 - 465 - 1) - i][2])
                avg = np.float64((r + g + b)) / 3
            if (avg / 10) > 4:
                p_count += 1
            if p_count > 15:
                print(f'boss_hp: {(((1460 - 465 - 1) - i) / (1460 - 465))}')
                break
        if p_count < 15:
            print('boss_hp:1')
    else:
        print('boss_hp : 1')
    #cv2.waitKey(1)