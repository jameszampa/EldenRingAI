import os
import cv2
import gym
import time
import requests
import subprocess
import numpy as np
import pytesseract
from gym import spaces
from tensorboardX import SummaryWriter
from EldenReward import EldenReward
import json

TOTAL_ACTIONABLE_TIME = 120

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

    def __init__(self, logdir):
        super(EldenEnv, self).__init__()
        # Define action and observation space
        # They must be gym.spaces objects
        # Example when using discrete actions:
        self.action_space = spaces.Discrete(N_DISCRETE_ACTIONS)
        # Example for using image as input (channel-first; channel-last also works):
        self.observation_space = spaces.Box(low=0, high=255,
                                            shape=(MODEL_HEIGHT, MODEL_WIDTH, N_CHANNELS), dtype=np.uint8)
        
        self.cap = cv2.VideoCapture('/dev/video0')
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, IMG_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, IMG_HEIGHT)
        self.agent_ip = '192.168.4.70'
        self.logger = SummaryWriter(os.path.join(logdir, 'PPO_0'))

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
        self.rewardGen = EldenReward(1, logdir)
        self.death = False
        self.t_start = None
        self.done = False
        self.iteration = 0
        self.first_step = False
        self.consecutive_deaths = 0
        self.locked_on = False
        self.num_runs = 0
        self.max_reward = None


    def step(self, action):
        json_message = {'text': 'Step'}
        headers = {"Content-Type": "application/json"}
        requests.post(f"http://{self.agent_ip}:6000/status/update", headers=headers, data=json.dumps(json_message))

        headers = {"Content-Type": "application/json"}
        requests.post(f"http://{self.agent_ip}:6000/action/focus_window", headers=headers)

        headers = {"Content-Type": "application/json"}
        requests.post(f"http://{self.agent_ip}:6000/action/release_keys", headers=headers)

        ret, frame = self.cap.read()
        if not ret:
            raise ValueError("Unable to capture ELDENRING frame")

        time_alive, percent_through, hp, self.death, dmg_reward, find_reward, time_since_boss_seen = self.rewardGen.update(frame)
        self.logger.add_scalar('time_alive', time_alive, self.iteration)
        self.logger.add_scalar('percent_through', percent_through, self.iteration)
        self.logger.add_scalar('hp', hp, self.iteration)
        self.logger.add_scalar('dmg_reward', dmg_reward, self.iteration)
        self.logger.add_scalar('find_reward', find_reward, self.iteration)
        self.reward = time_alive + percent_through + hp + dmg_reward + find_reward

        if not self.death:
            # Time limit for fighting Tree sentienel (600 seconds or 10 minutes)
            if (time.time() - self.t_start) > TOTAL_ACTIONABLE_TIME and self.rewardGen.time_since_seen_boss > 2.5:
                headers = {"Content-Type": "application/json"}
                requests.post(f"http://{self.agent_ip}:6000/action/return_to_grace", headers=headers)
                self.done = True
                self.reward = -10000000
                self.rewardGen.time_since_death = time.time()
            else:
                if not self.locked_on and time_since_boss_seen < 2.5:
                    headers = {"Content-Type": "application/json"}
                    requests.post(f"http://{self.agent_ip}:6000/action/lock_on", headers=headers)
                    self.locked_on = True

                if int(action) == 10 and (self.rewardGen.curr_hp / self.rewardGen.max_hp) >= 0.75:
                    pass
                else:
                    headers = {"Content-Type": "application/json"}
                    requests.post(f"http://{self.agent_ip}:6000/action/custom/{int(action)}", headers=headers)
                    #time.sleep(0.25)
                    self.consecutive_deaths = 0
        else:
            headers = {"Content-Type": "application/json"}
            # if we load in and die with 5 seconds, restart game because we are frozen on a black screen
            if self.first_step:
                self.consecutive_deaths += 1
                if self.consecutive_deaths > 5:
                    self.consecutive_deaths = 0
                    headers = {"Content-Type": "application/json"}
                    requests.post(f"http://{self.agent_ip}:6000/action/stop_elden_ring", headers=headers)
                    time.sleep(5 * 60)
                    headers = {"Content-Type": "application/json"}
                    requests.post(f"http://{self.agent_ip}:6000/action/start_elden_ring", headers=headers)
                    time.sleep(180)

                    headers = {"Content-Type": "application/json"}
                    requests.post(f"http://{self.agent_ip}:6000/action/focus_window", headers=headers)

                    headers = {"Content-Type": "application/json"}
                    requests.post(f"http://{self.agent_ip}:6000/action/load_save", headers=headers)

                    headers = {"Content-Type": "application/json"}
                    requests.post(f"http://{self.agent_ip}:6000/action/return_to_grace", headers=headers)
            else:
                requests.post(f"http://{self.agent_ip}:6000/action/death_reset", headers=headers)
            self.done = True
            
        observation = cv2.resize(frame, (MODEL_WIDTH, MODEL_HEIGHT))
        info = {}
        self.first_step = False
        self.iteration += 1
        self.logger.add_scalar('reward', self.reward, self.iteration)

        if not self.done:
            json_message = {"death": self.death,
                            "reward": self.reward,
                            "num_run": self.num_runs,
                            "lowest_boss_hp": self.rewardGen.min_boss_hp}

            requests.post(f"http://{self.agent_ip}:6000/obs/log", headers=headers, data=json.dumps(json_message))
            if self.max_reward is None:
                self.max_reward = self.reward
            elif self.max_reward < self.reward:
                self.max_reward = self.reward

        return observation, self.reward, self.done, info
    
    def reset(self):
        self.num_runs += 1
        headers = {"Content-Type": "application/json"}
        requests.post(f"http://{self.agent_ip}:6000/action/focus_window", headers=headers)

        headers = {"Content-Type": "application/json"}
        requests.post(f"http://{self.agent_ip}:6000/recording/stop", headers=headers)

        json_message = {'text': 'Check for frozen screen'}
        headers = {"Content-Type": "application/json"}
        requests.post(f"http://{self.agent_ip}:6000/status/update", headers=headers, data=json.dumps(json_message))

        # check frozen load screen
        reset = 0
        self.done = False
        for i in range(15):
            ret, frame = self.cap.read()

            parry_image = frame[675:710, 85:150]
            parry_image = cv2.resize(parry_image, (parry_image.shape[1]*5, parry_image.shape[0]*5))
            parry_text = pytesseract.image_to_string(parry_image,  lang='eng',config='--psm 6 --oem 3')
            if 'Parry' in parry_text:
                break

            next_text_image = frame[1015:1040, 155:205]
            next_text_image = cv2.resize(next_text_image, ((205-155)*3, (1040-1015)*3))
            next_text = pytesseract.image_to_string(next_text_image,  lang='eng',config='--psm 6 --oem 3')
            if "Next" in next_text:
                reset += 1

            # This didnt work :(
            lost_connection_image = frame[475:550, 675:1250]
            lost_connection_image = cv2.resize(lost_connection_image, ((1250-675)*3, (550-475)*3))
            lost_connection_text = pytesseract.image_to_string(lost_connection_image,  lang='eng',config='--psm 6 --oem 3')
            lost_connection_words = ["connection", "game", "server", "lost"]
            for word in lost_connection_words:
                if word in lost_connection_text:
                    reset += 1
                    break

            revive_loc_img = frame[800:850, 800:1100]
            revive_loc_img = cv2.resize(revive_loc_img, ((1100-800)*3, (850-800)*3))
            revive_loc_text = pytesseract.image_to_string(revive_loc_img,  lang='eng',config='--psm 6 --oem 3')
            revive_loc_words = ["Choose", "revival", "location"]
            for word in revive_loc_words:
                if word in revive_loc_text:
                    reset += 1
                    break
            time.sleep(1)
        
        
        if reset >= 12:
            headers = {"Content-Type": "application/json"}
            requests.post(f"http://{self.agent_ip}:6000/action/stop_elden_ring", headers=headers)
            time.sleep(5 * 60)
            headers = {"Content-Type": "application/json"}
            requests.post(f"http://{self.agent_ip}:6000/action/start_elden_ring", headers=headers)
            time.sleep(180)

            headers = {"Content-Type": "application/json"}
            requests.post(f"http://{self.agent_ip}:6000/action/focus_window", headers=headers)

            headers = {"Content-Type": "application/json"}
            requests.post(f"http://{self.agent_ip}:6000/action/load_save", headers=headers)

            headers = {"Content-Type": "application/json"}
            requests.post(f"http://{self.agent_ip}:6000/action/return_to_grace", headers=headers)


        headers = {"Content-Type": "application/json"}
        requests.post(f"http://{self.agent_ip}:6000/recording/tag_latest/{self.max_reward}/{self.num_runs}'", headers=headers)

        headers = {"Content-Type": "application/json"}
        requests.post(f"http://{self.agent_ip}:6000/recording/start", headers=headers)

        observation = cv2.resize(frame, (MODEL_WIDTH, MODEL_HEIGHT))
        self.t_start = time.time()
        self.done = False
        self.first_step = True
        self.locked_on = False
        self.rewardGen.curr_boss_hp = 3200
        self.max_reward = None
        self.rewardGen.seen_boss = False
        self.rewardGen.time_since_seen_boss = time.time()
        self.rewardGen.prev_hp = self.rewardGen.max_hp
        self.rewardGen.curr_hp = self.rewardGen.max_hp
        self.rewardGen.time_since_reset = time.time()

        headers = {"Content-Type": "application/json"}
        requests.post(f"http://{self.agent_ip}:6000/action/init_fight", headers=headers)

        return observation

    def render(self, mode='human'):
        pass

    def close (self):
        self.cap.release()





