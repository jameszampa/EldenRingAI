import os
import cv2
import gym
import time
import requests
import subprocess
import numpy as np
import pytesseract
from gym import spaces
from EldenReward import EldenReward


DISCRETE_ACTIONS = {'w': 'run_forwards',
                    's': 'run_backwards',
                    'a': 'run_left',
                    'd': 'run_right',
                    'release_wasd': 'release_wasd',
                    'space': 'dodge',
                    'm1': 'attack',
                    'shift+m1': 'strong_attack',
                    'm2': 'guard',
                    'shift+m2': 'skill',
                    'r': 'use_item',
                    'space_hold': 'sprint'}
                    #'e': 'event_action'}
                    # 'up': 'uparrow',
                    # 'down': 'downarrow',
                    # 'left': 'leftarrow',
                    # 'right': 'rightarrow',
                    # 'esc': 'esc'}

N_DISCRETE_ACTIONS = len(DISCRETE_ACTIONS)
N_CHANNELS = 3
IMG_WIDTH = 1920
IMG_HEIGHT = 1080
MODEL_HEIGHT = 450
MODEL_WIDTH = 800

HP_CHART = {}
with open('vigor_chart.csv', 'r') as v_chart:
    for line in v_chart.readlines():
        stat_point = int(line.split(',')[0])
        hp_amount = int(line.split(',')[1])
        HP_CHART[stat_point] = hp_amount
#print(HP_CHART)


class EldenEnv(gym.Env):
    """Custom Environment that follows gym interface"""

    def __init__(self):
        super(EldenEnv, self).__init__()
        # Define action and observation space
        # They must be gym.spaces objects
        # Example when using discrete actions:
        self.action_space = spaces.Discrete(N_DISCRETE_ACTIONS)
        # Example for using image as input (channel-first; channel-last also works):
        self.observation_space = spaces.Box(low=0, high=255,
                                            shape=(MODEL_HEIGHT, MODEL_WIDTH, N_CHANNELS), dtype=np.uint8)
        
        self.cap = cv2.VideoCapture('/dev/usb/hiddev1')
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, IMG_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, IMG_HEIGHT)
        self.agent_ip = '192.168.4.70'

        ret, _ = self.cap.read()
        if not ret:
            raise ValueError("Unable to find ELDEN RING camera")
        
        headers = {"Content-Type": "application/json"}
        requests.post(f"http://{self.agent_ip}:6000/action/start_elden_ring", headers=headers)
        time.sleep(180)

        headers = {"Content-Type": "application/json"}
        requests.post(f"http://{self.agent_ip}:6000/action/focus_window", headers=headers)

        headers = {"Content-Type": "application/json"}
        requests.post(f"http://{self.agent_ip}:6000/action/load_save", headers=headers)
        
        self.reward = 0
        self.rewardGen = EldenReward(1)
        self.death = False
        self.t_start = None
        self.done = False


    def step(self, action):
        headers = {"Content-Type": "application/json"}
        requests.post(f"http://{self.agent_ip}:6000/action/focus_window", headers=headers)

        headers = {"Content-Type": "application/json"}
        requests.post(f"http://{self.agent_ip}:6000/action/release_keys", headers=headers)

        ret, frame = self.cap.read()
        if not ret:
            raise ValueError("Unable to capture ELDENRING frame")

        runes, stat, hp, self.death, dmg_reward, find_reward = self.rewardGen.update(frame)
        self.reward = runes + stat + hp + dmg_reward + find_reward

        if not self.death:
            # Time limit for fighting Tree sentienel (600 seconds or 10 minutes)
            if time.time() - self.t_start > 120:
                headers = {"Content-Type": "application/json"}
                requests.post(f"http://{self.agent_ip}:6000/action/return_to_grace", headers=headers)
            else:
                headers = {"Content-Type": "application/json"}
                requests.post(f"http://{self.agent_ip}:6000/action/custom/{int(action)}", headers=headers)
        else:
            headers = {"Content-Type": "application/json"}
            requests.post(f"http://{self.agent_ip}:6000/action/death_reset", headers=headers)
            
        observation = cv2.resize(frame, (MODEL_WIDTH, MODEL_HEIGHT))
        info = {}
        
        return observation, self.reward, self.done, info
    
    def reset(self):
        headers = {"Content-Type": "application/json"}
        requests.post(f"http://{self.agent_ip}:6000/action/focus_window", headers=headers)

        # check frozen load screen
        reset = 0
        for i in range(10):
            ret, frame = self.cap.read()
            self.done = False

            next_text_image = frame[1015:1040, 155:205]
            next_text_image = cv2.resize(next_text_image, ((205-155)*3, (1040-1015)*3))
            next_text = pytesseract.image_to_string(next_text_image,  lang='eng',config='--psm 6 --oem 3')
            if "Next" in next_text:
                reset += 1
            time.sleep(1)

        if reset >= 8:
            headers = {"Content-Type": "application/json"}
            requests.post(f"http://{self.agent_ip}:6000/action/stop_elden_ring", headers=headers)
            time.sleep(120)
            headers = {"Content-Type": "application/json"}
            requests.post(f"http://{self.agent_ip}:6000/action/start_elden_ring", headers=headers)
            time.sleep(180)

            headers = {"Content-Type": "application/json"}
            requests.post(f"http://{self.agent_ip}:6000/action/focus_window", headers=headers)

            headers = {"Content-Type": "application/json"}
            requests.post(f"http://{self.agent_ip}:6000/action/load_save", headers=headers)

            headers = {"Content-Type": "application/json"}
            requests.post(f"http://{self.agent_ip}:6000/action/return_to_grace", headers=headers)

        observation = cv2.resize(frame, (MODEL_WIDTH, MODEL_HEIGHT))
        self.t_start = time.time()

        return observation

    def render(self, mode='human'):
        pass

    def close (self):
        self.cap.release()