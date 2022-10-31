import cv2
import numpy as np
import pytesseract
import time
import requests
import os
from tensorboardX import SummaryWriter

TOTAL_ACTIONABLE_TIME = 120
HP_CHART = {}

with open('vigor_chart.csv', 'r') as v_chart:
    for line in v_chart.readlines():
        stat_point = int(line.split(',')[0])
        hp_amount = int(line.split(',')[1])
        HP_CHART[stat_point] = hp_amount

class EldenReward:
    def __init__(self, char_slot, logdir, ip) -> None:
        self.previous_stats = None
        self.current_stats = None
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