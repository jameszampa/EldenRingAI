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

DISCRETE_ACTIONS = {'alt_w': 'walk_forwards',
                    'alt_s': 'walk_backwards',
                    'alt_a': 'walk_left',
                    'alt_d': 'walk_right',
                    'w': 'run_forwards',
                    's': 'run_backwards',
                    'a': 'run_left',
                    'd': 'run_right',
                    'q': 'lock_on',
                    'space': 'dodge',
                    'f': 'jump',
                    'x': 'crouch',
                    '1': 'switch_left_hand',
                    '2': 'switch_right_hand',
                    '3': 'switch_item',
                    '4': 'switch_sorcery',
                    'm1': 'attack',
                    'shift+m1': 'strong_attack',
                    'm2': 'guard',
                    'shift+m2': 'skill',
                    'r': 'use_item',
                    'e': 'event_action'}
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
        
        self.cap = cv2.VideoCapture(1)
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

        self.rewardGen = EldenReward(6)
        self.death = False


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
            # press keys according to action
            if action == 0:
                self.keyboard.press(kb.Key.alt_l)
                self.keys_pressed.append(kb.Key.alt_l)
                self.keyboard.press('w')
                self.keys_pressed.append('w')
            elif action == 1:
                self.keyboard.press(kb.Key.alt_l)
                self.keys_pressed.append(kb.Key.alt_l)
                self.keyboard.press('s')
                self.keys_pressed.append('s')
            elif action == 2:
                self.keyboard.press(kb.Key.alt_l)
                self.keys_pressed.append(kb.Key.alt_l)
                self.keyboard.press('a')
                self.keys_pressed.append('a')
            elif action == 3:
                self.keyboard.press(kb.Key.alt_l)
                self.keys_pressed.append(kb.Key.alt_l)
                self.keyboard.press('d')
                self.keys_pressed.append('d')
            elif action == 4:
                self.keyboard.press('w')
                self.keys_pressed.append('w')
            elif action == 5:
                self.keyboard.press('s')
                self.keys_pressed.append('s')
            elif action == 6:
                self.keyboard.press('a')
                self.keys_pressed.append('a')
            elif action == 7:
                self.keyboard.press('d')
                self.keys_pressed.append('d')
            elif action == 8:
                self.keyboard.press(kb.Key.space)
                self.keys_pressed.append(kb.Key.space)
            elif action == 9:
                self.keyboard.press('f')
                self.keys_pressed.append('f')
            elif action == 10:
                self.keyboard.press('x')
                self.keys_pressed.append('x')
            elif action == 11:
                self.keyboard.press('1')
                self.keys_pressed.append('1')
            elif action == 12:
                self.keyboard.press('2')
                self.keys_pressed.append('2')
            elif action == 13:
                self.keyboard.press('3')
                self.keys_pressed.append('3')
            elif action == 14:
                self.keyboard.press('4')
                self.keys_pressed.append('4')
            elif action == 15:
                self.keyboard.press('5')
                self.keys_pressed.append('5')
            elif action == 16:
                self.keyboard.press(kb.Key.shift_l)
                self.keys_pressed.append(kb.Key.shift_l)
                self.keyboard.press('5')
                self.keys_pressed.append('5')
            elif action == 17:
                self.keyboard.press('6')
                self.keys_pressed.append('6')
            elif action == 18:
                self.keyboard.press(kb.Key.shift_l)
                self.keys_pressed.append(kb.Key.shift_l)
                self.keyboard.press('6')
                self.keys_pressed.append('6')
            elif action == 19:
                self.keyboard.press('r')
                self.keys_pressed.append('r')
            elif action == 20:
                self.keyboard.press('e')
                self.keys_pressed.append('e')
            elif action == 21:
                self.keyboard.press(kb.Key.up)
                self.keys_pressed.append(kb.Key.up)
            elif action == 22:
                self.keyboard.press(kb.Key.down)
                self.keys_pressed.append(kb.Key.down)
            elif action == 23:
                self.keyboard.press(kb.Key.left)
                self.keys_pressed.append(kb.Key.left)
            elif action == 24:
                self.keyboard.press(kb.Key.right)
                self.keys_pressed.append(kb.Key.right)
            elif action == 25:
                self.keyboard.press(kb.Key.esc)
                self.keys_pressed.append(kb.Key.esc)

        observation = cv2.resize(frame, (MODEL_WIDTH, MODEL_HEIGHT))
        info = {}
        
        return observation, self.reward, self.done, info
    
    
    def reset(self):
        # Make sure elden ring is the active window
        self.w.set_foreground()

        ret, frame = self.cap.read()
        self.done = False

        observation = cv2.resize(frame, (MODEL_WIDTH, MODEL_HEIGHT))

        return observation

    def render(self, mode='human'):
        pass

    def close (self):
        self.cap.release()