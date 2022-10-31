import os
import cv2
import gym
import time
import requests
import numpy as np
import pytesseract
from gym import spaces
from tensorboardX import SummaryWriter
from EldenReward import EldenReward
import json
from threading import Thread
import cv2
import time
import os


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
                    'space_hold': 'sprint',
                    'f': 'jump'}

N_DISCRETE_ACTIONS = len(DISCRETE_ACTIONS)
N_CHANNELS = 3
IMG_WIDTH = 1920
IMG_HEIGHT = 1080
MODEL_HEIGHT = 450
MODEL_WIDTH = 800
CLASS_NAMES = ['successful_parries', 'missed_parries']
HP_CHART = {}
with open('vigor_chart.csv', 'r') as v_chart:
    for line in v_chart.readlines():
        stat_point = int(line.split(',')[0])
        hp_amount = int(line.split(',')[1])
        HP_CHART[stat_point] = hp_amount


class ThreadedCamera(object):
    def __init__(self, src=0):
        self.capture = cv2.VideoCapture(src)
        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 2)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, IMG_WIDTH)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, IMG_HEIGHT)
        (self.status, self.frame) = self.capture.read()
        # FPS = 1/X
        # X = desired FPS
        self.FPS = 1/30
        self.FPS_MS = int(self.FPS * 1000)
        
        # Start frame retrieval thread
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()
        
    def update(self):
        while True:
            if self.capture.isOpened():
                (self.status, self.frame) = self.capture.read()
            time.sleep(self.FPS)
            
    def show_frame(self):
        cv2.imshow('frame', self.frame)
        cv2.waitKey(self.FPS_MS)


class EldenEnv(gym.Env):
    """Custom Environment that follows gym interface"""

    def __init__(self, src, ip, logdir):
        super(EldenEnv, self).__init__()
        # Define action and observation space
        # They must be gym.spaces objects
        # Example when using discrete actions:
        self.action_space = spaces.Discrete(N_DISCRETE_ACTIONS)
        # Example for using image as input (channel-first; channel-last also works):
        self.observation_space = spaces.Box(low=0, high=255,
                                            shape=(MODEL_HEIGHT, MODEL_WIDTH, N_CHANNELS), dtype=np.uint8)

        self.cap = ThreadedCamera(src)
        self.agent_ip = ip
        self.logger = SummaryWriter(os.path.join(logdir, 'PPO_0'))
        
        headers = {"Content-Type": "application/json"}
        requests.post(f"http://{self.agent_ip}:6000/action/start_elden_ring", headers=headers)
        time.sleep(90)

        headers = {"Content-Type": "application/json"}
        requests.post(f"http://{self.agent_ip}:6000/action/focus_window", headers=headers)

        headers = {"Content-Type": "application/json"}
        requests.post(f"http://{self.agent_ip}:6000/action/load_save", headers=headers)
        
        self.reward = 0
        self.rewardGen = EldenReward(1, logdir)
        self.death = False
        self.t_start = time.time()
        self.done = False
        self.iteration = 0
        self.first_step = False
        self.consecutive_deaths = 0
        self.locked_on = False
        self.num_runs = 0
        self.max_reward = None
        self.time_since_r = time.time()
        self.reward_history = []
        self.parry_dict = {'vod_duration':None,
                           'parries': []}
        self.t_since_parry = None
        self.prev_step_end_ts = time.time()
        self.last_fps = []


    def step(self, action):
        t0 = time.time()
        if not self.first_step:
            self.logger.add_scalar('time_between_steps', t0 - self.prev_step_end_ts, self.iteration)
             
        headers = {"Content-Type": "application/json"}
        requests.post(f"http://{self.agent_ip}:6000/action/focus_window", headers=headers)
        requests.post(f"http://{self.agent_ip}:6000/action/release_keys", headers=headers)

        frame = self.cap.frame
        time_alive, percent_through, hp, self.death, dmg_reward, find_reward, _ = self.rewardGen.update(frame)

        self.logger.add_scalar('time_alive', time_alive, self.iteration)
        self.logger.add_scalar('percent_through', percent_through, self.iteration)
        self.logger.add_scalar('hp', hp, self.iteration)
        self.logger.add_scalar('dmg_reward', dmg_reward, self.iteration)
        self.logger.add_scalar('find_reward', find_reward, self.iteration)
        self.logger.add_scalar('parry_reward', 0, self.iteration)
        
        if hp > 0 and (time.time() - self.time_since_r) > 1.0:
            hp = 0

        self.reward = time_alive + percent_through + hp + dmg_reward + find_reward + 0

        if not self.death:
            # Time limit for fighting Tree sentienel (600 seconds or 10 minutes)
            if (time.time() - self.t_start) > TOTAL_ACTIONABLE_TIME and self.rewardGen.time_since_seen_boss > 2.5:
                headers = {"Content-Type": "application/json"}
                for i in range(10):
                    requests.post(f"http://{self.agent_ip}:6000/action/custom/{4}", headers=headers)
                    requests.post(f"http://{self.agent_ip}:6000/action/release_keys", headers=headers)
                    time.sleep(0.1)
                requests.post(f"http://{self.agent_ip}:6000/action/return_to_grace", headers=headers)
                self.done = True
                self.reward = -1
                self.rewardGen.time_since_death = time.time()
            else:
                if int(action) == 10 and (self.rewardGen.curr_hp / self.rewardGen.max_hp) >= 0.5:
                    pass
                else:
                    if int(action) == 10:
                        self.time_since_r = time.time()
                    headers = {"Content-Type": "application/json"}
                    requests.post(f"http://{self.agent_ip}:6000/action/custom/{int(action)}", headers=headers)
                    
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
                headers = {"Content-Type": "application/json"}
                for i in range(10):
                    requests.post(f"http://{self.agent_ip}:6000/action/custom/{4}", headers=headers)
                    requests.post(f"http://{self.agent_ip}:6000/action/release_keys", headers=headers)
                    time.sleep(0.1)

            self.done = True
        observation = cv2.resize(frame, (MODEL_WIDTH, MODEL_HEIGHT))
        info = {}
        self.first_step = False
        self.iteration += 1

        if self.reward < -1:
            self.reward = -1
        if self.reward > 1:
            self.reward = 1

        if self.max_reward is None:
            self.max_reward = self.reward
        elif self.max_reward < self.reward:
            self.max_reward = self.reward

        self.logger.add_scalar('reward', self.reward, self.iteration)
        self.reward_history.append(self.reward)

        t_end = time.time()
        self.last_fps.append(1 / (t_end - t0))
        desired_fps = (1 / 15)
        time_to_sleep = desired_fps - (t_end - t0)
        if time_to_sleep > 0:
            time.sleep(time_to_sleep)
        self.logger.add_scalar('step_time', (time.time() - t0), self.iteration)
        self.prev_step_end_ts = time.time()
        return observation, self.reward, self.done, info
    
    def reset(self):
        self.done = False
        time.sleep(5)
        self.num_runs += 1
        self.logger.add_scalar('iteration_finder', self.iteration, self.num_runs)

        headers = {"Content-Type": "application/json"}
        requests.post(f"http://{self.agent_ip}:6000/action/focus_window", headers=headers)

        json_message = {'text': 'Check for frozen screen'}
        headers = {"Content-Type": "application/json"}
        requests.post(f"http://{self.agent_ip}:6000/status/update", headers=headers, data=json.dumps(json_message))

        avg_fps = 0
        for i in range(len(self.last_fps)):
            avg_fps += self.last_fps[i]
        self.last_fps = []
        if len(self.last_fps) > 0:
            avg_fps = avg_fps / len(self.last_fps)
        self.logger.add_scalar('avg_fps', avg_fps, self.num_runs)

        frame = self.cap.frame
        next_text_image = frame[1015:1040, 155:205]
        next_text_image = cv2.resize(next_text_image, ((205-155)*3, (1040-1015)*3))
        next_text = pytesseract.image_to_string(next_text_image,  lang='eng',config='--psm 6 --oem 3')
        loading_screen = "Next" in next_text
        loading_screen_history = []
        min_look = 30
        time.sleep(2)
        while True:
            frame = self.cap.frame

            next_text_image = frame[1015:1040, 155:205]
            next_text_image = cv2.resize(next_text_image, ((205-155)*3, (1040-1015)*3))
            next_text = pytesseract.image_to_string(next_text_image,  lang='eng',config='--psm 6 --oem 3')
            loading_screen = "Next" in next_text
            time.sleep(1/30)
            loading_screen_history.append(loading_screen)
            if len(loading_screen_history) > min_look:
                all_false = True
                for i in range(5):
                    if loading_screen_history[-(i + 1)]:
                        all_false = False
                if all_false:
                    break
                if len(loading_screen_history) > 30*30:
                    break

        lost_connection_image = frame[475:550, 675:1250]
        lost_connection_image = cv2.resize(lost_connection_image, ((1250-675)*3, (550-475)*3))
        lost_connection_text = pytesseract.image_to_string(lost_connection_image,  lang='eng',config='--psm 6 --oem 3')
        lost_connection_words = ["connection", "game", "server", "lost"]
        lost_connection = False
        for word in lost_connection_words:
            if word in lost_connection_text:
                lost_connection = True
        
        if len(loading_screen_history) > 30*30 or lost_connection:
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
        

        observation = cv2.resize(frame, (MODEL_WIDTH, MODEL_HEIGHT))
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
        self.rewardGen.boss_hp = 1
        if len(self.reward_history) > 0:
            total_r = 0
            for r in self.reward_history:
                total_r += r
            avg_r = total_r / len(self.reward_history)
            self.logger.add_scalar('average_reward_per_run', avg_r, self.num_runs)
        self.reward_history = []
        self.parry_dict = {'vod_duration':None,
                           'parries': []}


        headers = {"Content-Type": "application/json"}
        requests.post(f"http://{self.agent_ip}:6000/action/focus_window", headers=headers)

        self.t_start = time.time()

        headers = {"Content-Type": "application/json"}
        requests.post(f"http://{self.agent_ip}:6000/action/init_fight", headers=headers)

        json_message = {'text': 'Step'}
        headers = {"Content-Type": "application/json"}
        requests.post(f"http://{self.agent_ip}:6000/status/update", headers=headers, data=json.dumps(json_message))

        return observation

    def render(self, mode='human'):
        pass

    def close (self):
        self.cap.release()