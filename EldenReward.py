import cv2
import json
import numpy as np
import pytesseract
import time
import requests
from EldenEnv import TOTAL_ACTIONABLE_TIME

HP_CHART = {}
with open('vigor_chart.csv', 'r') as v_chart:
    for line in v_chart.readlines():
        stat_point = int(line.split(',')[0])
        hp_amount = int(line.split(',')[1])
        HP_CHART[stat_point] = hp_amount


class EldenReward:
    def __init__(self, char_slot) -> None:
        self.previous_runes_held = None
        self.current_runes_held = None

        self.previous_stats = None
        self.current_stats = None
        self.seen_boss = False

        self.max_hp = None
        self.prev_hp = None
        self.curr_hp = None

        self.hp_ratio = 0.403

        self.character_slot = char_slot

        self.death_ratio = 0.11

        self.time_since_death = None
        self.time_since_seen_boss = None

        self.death = False
        self.curr_boss_hp = None
        self.prev_boss_hp = None

        self.agent_ip = '192.168.4.70'
        self._request_stats()


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


    def _get_runes_held(self, frame):
        runes_image = frame[1020:1050, 1715:1868]
        runes_image = cv2.resize(runes_image, (154*3, 30*3))
        runes_held = pytesseract.image_to_string(runes_image,  lang='eng',config='--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789')
        if runes_held != "":
            return int(runes_held)
        else:
            return self.previous_runes_held


    def _get_boss_name(self, frame):
        boss_name = frame[842:860, 450:650]
        boss_name = cv2.resize(boss_name, ((650-450)*3, (860-842)*3))
        boss_name = pytesseract.image_to_string(boss_name,  lang='eng',config='--psm 6 --oem 3')
        if boss_name != "":
            return boss_name
        else:
            return None

    
    def _get_boss_dmg(self, frame):
        boss_dmg = frame[840:860, 1410:1480]
        boss_dmg = cv2.resize(boss_dmg, ((1480-1410)*3, (860-840)*3))
        boss_dmg = pytesseract.image_to_string(boss_dmg,  lang='eng',config='--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789')
        if boss_dmg != "":
            return int(boss_dmg)
        else:
            return 0

        
    def update(self, frame):
        # self.previous_runes_held = self.current_runes_held
        # try:
        #     self.current_runes_held = self._get_runes_held(frame)
        # except:
        #     pass
        
        # if not self.previous_runes_held is None and not self.current_runes_held is None:
        #     runes_reward = self.current_runes_held - self.previous_runes_held
        # else:
        #     runes_reward = 0

        if self.curr_hp is None:
            self.curr_hp = self.max_hp
        stat_reward = 0
        # if not self.previous_stats is None and not self.current_stats is None:
        #     if runes_reward < 0:
                # self._request_stats()
                # for i, stat in enumerate(self.current_stats):
                #     if self.current_stats[i] != self.previous_stats[i]:
                #         stat_reward += (self.current_stats[i] - self.previous_stats[i]) * 10000
        
        hp_reward = 0
        if not self.death:
            hp_image = frame[45:55, 155:155 + int(self.max_hp * self.hp_ratio)]
            p_count = 0
            for i in range(int(self.max_hp * self.hp_ratio)):
                    avg = 0
                    for j in range(10):
                        r = np.float64(hp_image[j, i][0])
                        g = np.float64(hp_image[j, i][1])
                        b = np.float64(hp_image[j, i][2])
                        avg = np.float64((r + g + b)) / 3
                    if i > 2:
                        if avg < 40:
                            p_count += 1
                    
                    if p_count > 10:
                        self.prev_hp = self.curr_hp
                        self.curr_hp = (i / int(self.max_hp * self.hp_ratio)) * self.max_hp
                        if not self.prev_hp is None and not self.curr_hp is None:
                            hp_reward += (self.curr_hp - self.prev_hp) * 10
                        break
            
            # if p_count < 10:
            #     self.prev_hp = self.curr_hp
            #     self.curr_hp = self.max_hp

        if self.death:
            time_alive = time.time() - self.time_since_death
            if time_alive > TOTAL_ACTIONABLE_TIME:
                time_alive = TOTAL_ACTIONABLE_TIME
            hp_reward = -((TOTAL_ACTIONABLE_TIME - (time_alive)) / TOTAL_ACTIONABLE_TIME) * 100

        if not self.death and not self.curr_hp is None:
            self.death = (self.curr_hp / self.max_hp) < self.death_ratio
            if self.death:
                self.time_since_death = time.time()

        if self.death:
            if (time.time() - self.time_since_death) > 25:
                self.curr_hp = self.max_hp
                self.death = False

        boss_name = self._get_boss_name(frame)
        boss_dmg_reward = 0
        boss_find_reward = 0
        boss_timeout = 2.5
        # set_hp = False
        if not boss_name is None and 'Tree Sentinel' in boss_name:
            self.seen_boss = True
            self.time_since_seen_boss = time.time()
        
        if (time.time() - self.time_since_seen_boss) < boss_timeout:
            time_since_boss = time.time() - self.time_since_seen_boss
            if time_since_boss < boss_timeout:
                boss_find_reward = ((boss_timeout - time_since_boss) / boss_timeout) * 100
            else:
                boss_find_reward = -time_since_boss * 25
            
            try:
                boss_dmg_reward = self._get_boss_dmg(frame) * 10000
            except:
                pass

        return 0, 0, 0, self.death, boss_dmg_reward, boss_find_reward