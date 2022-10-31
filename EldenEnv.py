import os
import cv2
import gym
import time
import json
import requests
import numpy as np
import pytesseract
from gym import spaces
from threading import Thread
from stable_baselines3 import PPO
from tensorboardX import SummaryWriter


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


class EldenReward:
    def __init__(self, char_slot, logdir, ip) -> None:
        self.seen_boss = False

        self.max_hp = None
        self.prev_hp = None
        self.curr_hp = None

        self.hp_ratio = 0.403

        self.character_slot = char_slot

        self.death_ratio = 0.005

        self.time_since_death = time.time()
        self.time_since_seen_boss = time.time()

        self.death = False

        self.agent_ip = ip
        self._request_stats()
        self.logger = SummaryWriter(os.path.join(logdir, 'PPO_0'))
        self.iteration = 0
        self.boss_hp = None
        self.time_since_last_hp_change = time.time()
        self.time_since_last_boss_hp_change = time.time()
        self.boss_hp_history = []
        self.boss_hp_target_range = 10
        self.boss_hp_target_window = 5
        self.time_till_fight = 120
        self.time_since_reset = time.time()
        self.min_boss_hp = 1
        self.time_since_check_for_boss = time.time()
        

    def _request_stats(self):
        headers = {"Content-Type": "application/json"}
        response = requests.get(f"http://{self.agent_ip}:6000/stats/{self.character_slot}", headers=headers)
        stats = response.json()
        #print(stats)

        self.previous_stats = self.current_stats
        self.current_stats = [stats['vigor'],
                              stats['mind'],
                              stats['endurance'],
                              stats['strength'],
                              stats['dexterity'],
                              stats['intelligence'],
                              stats['faith'],
                              stats['arcane']]
        self.max_hp = HP_CHART[self.current_stats[0]]
        self.time_alive_multiplier = 1


    def _get_boss_name(self, frame):
        boss_name = frame[842:860, 450:650]
        boss_name = cv2.resize(boss_name, ((650-450)*3, (860-842)*3))
        boss_name = pytesseract.image_to_string(boss_name,  lang='eng',config='--psm 6 --oem 3')
        if boss_name != "":
            return boss_name
        else:
            return None

        
    def update(self, frame):
        self.iteration += 1

        if self.curr_hp is None:
            self.curr_hp = self.max_hp

        hp_reward = 0
        if not self.death:
            t0 = time.time()
            hp_image = frame[51:55, 155:155 + int(self.max_hp * self.hp_ratio) - 20]
            lower = np.array([0,150,95])
            upper = np.array([150,255,125])
            hsv = cv2.cvtColor(hp_image, cv2.COLOR_RGB2HSV)
            mask = cv2.inRange(hsv, lower, upper)
            matches = np.argwhere(mask==255)
            self.prev_hp = self.curr_hp
            self.curr_hp = (len(matches) / (hp_image.shape[1] * hp_image.shape[0])) * self.max_hp

            # check for 1 hp
            if (self.curr_hp / self.max_hp) < self.death_ratio:
                lower = np.array([0,0,150])
                upper = np.array([255,255,255])
                hsv = cv2.cvtColor(hp_image, cv2.COLOR_RGB2HSV)
                mask = cv2.inRange(hsv, lower, upper)
                matches = np.argwhere(mask==255)
                self.prev_hp = self.curr_hp
                self.curr_hp = (len(matches) / (hp_image.shape[1] * hp_image.shape[0])) * self.max_hp
            
            t1 = time.time()
            if not self.prev_hp is None and not self.curr_hp is None:
                hp_reward = (self.curr_hp - self.prev_hp) / self.max_hp
                if hp_reward != 0:
                    self.time_since_last_hp_change = time.time()
                if hp_reward > 0:
                    hp_reward /= 8

            boss_name = ""
            if not self.seen_boss and time.time() - self.time_since_check_for_boss > 2:
                boss_name = self._get_boss_name(frame)
                self.time_since_check_for_boss = time.time()

            boss_dmg_reward = 0
            boss_find_reward = 0
            boss_timeout = 2.5
            # set_hp = False
            if not boss_name is None and 'Tree Sentinel' in boss_name:
                if not self.seen_boss:
                    self.time_till_fight = 1 - ((time.time() - self.time_since_reset) / TOTAL_ACTIONABLE_TIME)
                self.seen_boss = True
                self.time_since_seen_boss = time.time()
            
            if not self.time_since_seen_boss is None:
                time_since_boss = time.time() - self.time_since_seen_boss
                if time_since_boss < boss_timeout:
                    if not self.seen_boss:
                        boss_find_reward = -time_since_boss / TOTAL_ACTIONABLE_TIME
                    else:
                        boss_find_reward = 0
                else:
                    boss_find_reward = -time_since_boss / TOTAL_ACTIONABLE_TIME
                
        self.logger.add_scalar('curr_hp', self.curr_hp / self.max_hp, self.iteration)
        
        boss_hp = 1
        if self.seen_boss and not self.death:
            boss_hp_image = frame[869:873, 475:1460]
            lower = np.array([100,0,0])
            upper = np.array([150,255,255])
            hsv = cv2.cvtColor(boss_hp_image, cv2.COLOR_RGB2HSV)
            mask = cv2.inRange(hsv, lower, upper)
            matches = np.argwhere(mask==255)
            boss_hp = len(matches) / (boss_hp_image.shape[1] * boss_hp_image.shape[0])

        if self.boss_hp is None:
            self.boss_hp = 1

        if abs(boss_hp - self.boss_hp) < 0.08 and self.time_since_last_boss_hp_change > 1.0:
            boss_dmg_reward = (self.boss_hp - boss_hp) * 15
            if boss_dmg_reward < 0:
                boss_dmg_reward = 0
            self.boss_hp = boss_hp
            self.boss_hp_history.append(self.boss_hp)
            self.time_since_last_boss_hp_change = time.time()

        percent_through_fight_reward = 0
        if not self.death:
            if len(self.boss_hp_history) >= self.boss_hp_target_window:
                boss_max = None
                boss_min = None
                for i in range(self.boss_hp_target_window):
                    if boss_max is None:
                        boss_max = self.boss_hp_history[-(i + 1)]
                    elif boss_max < self.boss_hp_history[-(i + 1)]:
                        boss_max = self.boss_hp_history[-(i + 1)]
                    if boss_min is None:
                        boss_min = self.boss_hp_history[-(i + 1)]
                    elif boss_min > self.boss_hp_history[-(i + 1)]:
                        boss_min = self.boss_hp_history[-(i + 1)]
                if abs(boss_max - boss_min) < self.boss_hp_target_range:
                    percent_through_fight_reward = (1 - self.boss_hp) * 0.5
                    self.time_alive_multiplier = 1 - self.boss_hp
                    if self.boss_hp < self.min_boss_hp:
                        self.min_boss_hp = self.boss_hp
                else:
                    percent_through_fight_reward = 0
            else:
                percent_through_fight_reward = 0
        else:
            percent_through_fight_reward = 0
        self.logger.add_scalar('boss_hp', self.boss_hp, self.iteration)

        if not self.death and not self.curr_hp is None:
            self.death = (self.curr_hp / self.max_hp) <= self.death_ratio
            time_alive = time.time() - self.time_since_death
            if self.seen_boss:
                time_alive_reward = (time_alive * 0.001) * (self.time_alive_multiplier)
            else:
                time_alive_reward = 0
            if self.death:
                hp_reward = -1
                self.time_since_death = time.time()
                self.death = False
                self.seen_boss = False
                self.time_since_last_hp_change = time.time()
                self.boss_hp_history = []
                return time_alive_reward, percent_through_fight_reward, hp_reward, True, boss_dmg_reward, boss_find_reward, self.time_since_seen_boss
            else:
                return time_alive_reward, percent_through_fight_reward, hp_reward, self.death, boss_dmg_reward, boss_find_reward, self.time_since_seen_boss

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

ts = time.time()
models_dir = f"models/{int(ts)}/"
logdir = f"logs/{int(ts)}/"

if not os.path.exists(models_dir):
	os.makedirs(models_dir)

if not os.path.exists(logdir):
	os.makedirs(logdir)

env = EldenEnv(logdir)
env.reset()

model = PPO('MlpPolicy', env, verbose=1, tensorboard_log=logdir)

TIMESTEPS = 100000000
iters = 0
while True:
	iters += 1
	model.learn(total_timesteps=TIMESTEPS, reset_num_timesteps=False, tb_log_name=f"PPO")
	model.save(f"{models_dir}/{TIMESTEPS*iters}")