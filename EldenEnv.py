import gym
from gym import spaces
import numpy as np
import cv2
from WindowManager import WindowMgr
import pytesseract
import time
from pynput import keyboard as kb
from get_levels import get_stats

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
                    'e': 'event_action',
                    'up': 'uparrow',
                    'down': 'downarrow',
                    'left': 'leftarrow',
                    'right': 'rightarrow',
                    'esc': 'esc'}


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
        print(frame.shape)
        if not ret:
            raise ValueError("Unable to find ELDEN RING")
        # cv2.imshow('THE VIDEO GAME', frame)
        # cv2.waitKey(1)
        
        self.w = WindowMgr()
        self.w.find_window_wildcard('ELDEN RING.*')
        self.w.set_foreground()

        self.keyboard = kb.Controller()
        self.keys_pressed = []

        self.previous_runes_held = None
        self.current_runes_held = None
        self.reward = 0
        self.current_stats = None
        self.previous_stats = None
        self.character_slot = 6
        self.max_hp = None
        self.curr_hp = None
        self.prev_hp = None
        self.hp_ratio = 0.403

    def step(self, action):
        # Make sure elden ring is the active window
        self.w.set_foreground()

        # unpress any pressed keys
        for key in self.keys_pressed:
            self.keyboard.release(key)
        self.keys_pressed = []

        # self.keyboard.press(kb.Key.esc)
        # time.sleep(ESC_TIME)
        # self.keyboard.release(kb.Key.esc)
        # time.sleep(ESC_TIME)
        
        ret, frame = self.cap.read()

        # self.keyboard.press(kb.Key.esc)
        # time.sleep(ESC_TIME)
        # self.keyboard.release(kb.Key.esc)
        
        if not ret:
            raise ValueError("Unable to capture ELDENRING frame")

        runes_image = frame[1020:1050, 1715:1868]
        #print(runes_image.shape)
        runes_image = cv2.resize(runes_image, (154*3, 30*3))
        runes_held = pytesseract.image_to_string(runes_image,  lang='eng',config='--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789')
        # print("Runes Held: {}".format(runes_held))
        #print(runes_held)
        if runes_held != "":
            self.previous_runes_held = self.current_runes_held
            self.current_runes_held = int(runes_held)
            if not self.previous_runes_held is None and not self.current_runes_held is None:
                
                self.reward = self.current_runes_held - self.previous_runes_held
                print('Runes Reward!', self.reward)
            else:
                self.reward = 0
        else:
            self.reward = 0

        time.sleep(0.15)

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

        stats = get_stats(self.character_slot)
        self.previous_stats = self.current_stats
        self.current_stats = stats
        # print("current_stats: {}".format(self.curr))
        #print(self.current_stats)
        self.max_hp = HP_CHART[self.current_stats[0]]
        if not self.previous_stats is None and not self.current_stats is None:
            for i, stat in enumerate(self.current_stats):
                if self.current_stats[i] != self.previous_stats[i]:
                    self.reward += (self.current_stats[i] - self.previous_stats[i]) * 10000
                    print("LevelUp Reward!", self.reward)
        #time.sleep(0.5)

        hp_image = frame[45:55, 155:155 + int(self.max_hp * self.hp_ratio)]
        p_count = 0
        for i in range(int(self.max_hp * self.hp_ratio)):
                avg = 0
                for j in range(10):
                    r = np.float64(hp_image[j, i][0])
                    g = np.float64(hp_image[j, i][1])
                    b = np.float64(hp_image[j, i][2])
                    avg = np.float64((r + g + b)) / 3
                #print(i, avg)
                if i > 2:
                    if avg < 40:
                        p_count += 1
                
                if p_count > 10:
                    self.prev_hp = self.curr_hp
                    self.curr_hp = (i / int(self.max_hp * self.hp_ratio)) * self.max_hp
                    if not self.prev_hp is None and not self.curr_hp is None:
                        self.reward += (self.curr_hp - self.prev_hp) * 10
                        print("HP Reward", self.reward)
                        print(self.curr_hp / self.max_hp)
                    break
        
        return observation, self.reward, self.done, info
    
    
    def reset(self):
        # Make sure elden ring is the active window
        self.w.set_foreground()

        self.keyboard.press(kb.Key.esc)
        time.sleep(ESC_TIME)
        #self.keyboard.release(kb.Key.esc)

        ret, frame = self.cap.read()
        self.done = False

        self.keyboard.press(kb.Key.esc)
        #time.sleep(ESC_TIME)
        #self.keyboard.release(kb.Key.esc)

        #cv2.imshow('THE VIDEO GAME', frame)
        #cv2.waitKey(1)

        if not ret:
            raise ValueError("Unable to capture ELDENRING frame")

        runes_image = frame[1020:1050, 1715:1868]
        #print(runes_image.shape)
        runes_image = cv2.resize(runes_image, (154*3, 30*3))
        runes_held = pytesseract.image_to_string(runes_image,  lang='eng',config='--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789')
        #print("Runes Held: {}".format(runes_held))
        #print(runes_held)
        if runes_held != "":
            self.previous_runes_held = self.current_runes_held
            self.current_runes_held = int(runes_held)
            if not self.previous_runes_held is None and not self.current_runes_held is None:
                self.reward = self.current_runes_held - self.previous_runes_held
            else:
                self.reward = 0
        else:
            self.reward = 0


        observation = cv2.resize(frame, (MODEL_WIDTH, MODEL_HEIGHT))

        return observation

    def render(self, mode='human'):
        pass

    def close (self):
        self.cap.release()