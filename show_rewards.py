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
    
    
    loading_screen_history = []
    max_loading_screen_len = 30 * 15
    time.sleep(2)
    t_check_frozen_start = time.time()
    while True:
        frame = grab_screen_shot(sct)
        next_text_image = frame[1015:1040, 155:205]
        next_text_image = cv2.resize(next_text_image, ((205-155)*3, (1040-1015)*3))
        cv2.imshow('data', next_text_image)
        cv2.waitKey(1)
        next_text = pytesseract.image_to_string(next_text_image,  lang='eng',config='--psm 6 --oem 3')
        loading_screen = "Next" in next_text
        print("isNext:", loading_screen)
        loading_screen_history.append(loading_screen)
        if ((time.time() - t_check_frozen_start) > 7.5) and len(loading_screen_history) > 5:
            all_false = True
            for i in range(5):
                if loading_screen_history[-(i + 1)]:
                    all_false = False
            if all_false:
                break
            if len(loading_screen_history) > (max_loading_screen_len):
                break

    print(f"FPS: {1 / (time.time() - t0)}")
    #cv2.waitKey(1)