import cv2
from EldenReward import EldenReward
import time

cap = cv2.VideoCapture('/dev/video0')
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)


rewardGen = EldenReward(1)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    runes, stat, hp, death, dmg_reward, find_reward = rewardGen.update(frame)
    print("Runes:", runes)
    print("Stat:", stat)
    print("HP:", hp)
    print("dead:", death)
    print('dmg_reward', dmg_reward)
    print('find_reward', find_reward)
    print(rewardGen.current_stats)
    cv2.imshow('er', frame[840:860, 1410:1480])
    cv2.waitKey(1)