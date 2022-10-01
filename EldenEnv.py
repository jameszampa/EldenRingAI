import gym
from gym import spaces
import numpy as np
import cv2
from WindowManager import WindowMgr
import pytesseract
import time
from pynput import keyboard as kb
from get_levels import get_stats
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
ESC_TIME = 0.25

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
        
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, IMG_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, IMG_HEIGHT)

        ret, frame = self.cap.read()
        # print(frame.shape)
        if not ret:
            raise ValueError("Unable to find ELDEN RING")
        # cv2.imshow('THE VIDEO GAME', frame)
        # cv2.waitKey(1)
        
        self.w = WindowMgr()
        self.w.find_window_wildcard('ELDEN RING.*')
        self.w.set_foreground()

        self.keyboard = kb.Controller()
        self.keys_pressed = []

        self.reward = 0

        self.rewardGen = EldenReward(1)
        self.death = False

        self.t_start = None


    def step(self, action):
        # Make sure elden ring is the active window
        self.w.set_foreground()

        # unpress any pressed keys
        for key in self.keys_pressed:
            self.keyboard.release(key)
        self.keys_pressed = []
        
        ret, frame = self.cap.read()

        # self.keyboard.press(kb.Key.esc)
        # time.sleep(ESC_TIME)
        # self.keyboard.release(kb.Key.esc)
        
        if not ret:
            raise ValueError("Unable to capture ELDENRING frame")

        runes, stat, hp, self.death, dmg_reward, find_reward = self.rewardGen.update(frame)

        self.reward = runes + stat + hp + dmg_reward + find_reward

        if not self.death:
            # Time limit for fighting Tree sentienel (600 seconds or 10 minutes)
            if time.time() - self.t_start > 120:
                self.keyboard.press('e')
                self.keyboard.press('4')
                time.sleep(0.05)
                self.keyboard.release('e')
                self.keyboard.release('4')

                time.sleep(0.05)

                self.keyboard.press(kb.Key.left)
                time.sleep(0.05)
                self.keyboard.release(kb.Key.left)

                time.sleep(0.05)

                self.keyboard.press('e')
                time.sleep(0.05)
                self.keyboard.release('e')

                time.sleep(10)
                self.done = True
            # press keys according to action
            if action == 0:
                self.keyboard.release('w')
                self.keyboard.release('s')
                self.keyboard.press('w')
                # self.keys_pressed.append('w')
            elif action == 1:
                self.keyboard.release('w')
                self.keyboard.release('s')
                self.keyboard.press('s')
                # self.keys_pressed.append('s')
            elif action == 2:
                self.keyboard.release('a')
                self.keyboard.release('d')
                self.keyboard.press('a')
                # self.keys_pressed.append('a')
            elif action == 3:
                self.keyboard.release('a')
                self.keyboard.release('d')
                self.keyboard.press('d')
                # self.keys_pressed.append('d')
            elif action == 4:
                self.keyboard.release('w')
                self.keyboard.release('s')
                self.keyboard.release('a')
                self.keyboard.release('d')
            elif action == 5:
                self.keyboard.press(kb.Key.space)
                time.sleep(0.05)
                self.keyboard.release(kb.Key.space)
            elif action == 6:
                self.keyboard.press('5')
                self.keys_pressed.append('5')
            elif action == 7:
                self.keyboard.press(kb.Key.shift_l)
                self.keys_pressed.append(kb.Key.shift_l)
                self.keyboard.press('5')
                self.keys_pressed.append('5')
            elif action == 8:
                self.keyboard.press('6')
                self.keys_pressed.append('6')
                time.sleep(0.5)
            elif action == 9:
                self.keyboard.press(kb.Key.shift_l)
                self.keys_pressed.append(kb.Key.shift_l)
                self.keyboard.press('6')
                self.keys_pressed.append('6')
            elif action == 10:
                self.keyboard.press('r')
                self.keys_pressed.append('r')
            elif action == 11:
                self.keyboard.press(kb.Key.space)
                self.keys_pressed.append(kb.Key.space)
                time.sleep(0.5)
        else:
            self.keyboard.release('w')
            self.keyboard.release('s')
            self.keyboard.release('a')
            self.keyboard.release('d')
            time.sleep(10)
            self.done = True

        observation = cv2.resize(frame, (MODEL_WIDTH, MODEL_HEIGHT))
        info = {}
        
        return observation, self.reward, self.done, info
    
    
    def reset(self):
        # Make sure elden ring is the active window
        self.w.set_foreground()

        ret, frame = self.cap.read()
        self.done = False

        observation = cv2.resize(frame, (MODEL_WIDTH, MODEL_HEIGHT))

        self.t_start = time.time()

        return observation

    def render(self, mode='human'):
        pass

    def close (self):
        self.cap.release()