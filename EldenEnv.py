import os
import re
import cv2
import gym
import time
import json
import wave
import pyaudio
import requests
import datetime
import threading
import numpy as np
import pytesseract
import subprocess
from gym import spaces
import tensorflow as tf
from mss.linux import MSS as mss
from pynput import keyboard as kb
from EldenReward import EldenReward
from tensorboardX import SummaryWriter


HORIZON_WINDOW = 3000

gpus = tf.config.list_physical_devices('GPU')
if gpus:
  # Restrict TensorFlow to only use the first GPU
  try:
    tf.config.set_visible_devices(gpus[0], 'GPU')
    tf.config.experimental.set_memory_growth(gpus[0], True)
    logical_gpus = tf.config.list_logical_devices('GPU')
    print(len(gpus), "Physical GPUs,", len(logical_gpus), "Logical GPU")
  except RuntimeError as e:
    # Visible devices must be set before GPUs have been initialized
    print(e)


TOTAL_ACTIONABLE_TIME = 120

DISCRETE_ACTIONS = {'w': 'run_forwards',
                    's': 'run_backwards',
                    'a': 'run_left',
                    'd': 'run_right',
                    'release_wasd': 'release_wasd',
                    'space': 'dodge',
                    'm1': 'attack',
                    'shift+m1': 'strong_attack',
                    'r': 'use_item'}

N_DISCRETE_ACTIONS = len(DISCRETE_ACTIONS)
N_CHANNELS = 3
IMG_WIDTH = 1920
IMG_HEIGHT = 1080
MODEL_HEIGHT = int(450 / 2)
MODEL_WIDTH = int(800 / 2)
NUM_ACTION_HISTORY = 30 * 5
CLASS_NAMES = ['successful_parries', 'missed_parries']
HP_CHART = {}

elden_agent_keyboard = kb.Controller()

with open('vigor_chart.csv', 'r') as v_chart:
    for line in v_chart.readlines():
        stat_point = int(line.split(',')[0])
        hp_amount = int(line.split(',')[1])
        HP_CHART[stat_point] = hp_amount
#print(HP_CHART)


def timer_callback(t_start):
    while True:
        duration = time.gmtime(time.time() - t_start)
        days = int(np.floor((time.time() - t_start) / (24 * 60 * 60)))
        out_str = str(days).zfill(2) + ":"
        out_str += str(time.strftime('%H:%M:%S', duration))
        headers = {"Content-Type": "application/json"}
        json_message = {'timer':out_str}
        requests.post(f"http://192.168.4.67:6000/obs/log/timer_update", headers=headers, data=json.dumps(json_message))
        time.sleep(1)



def audio_to_fft(audio):
    # Since tf.signal.fft applies FFT on the innermost dimension,
    # we need to squeeze the dimensions and then expand them again
    # after FFT
    audio = tf.squeeze(audio, axis=-1)
    fft = tf.signal.fft(
        tf.cast(tf.complex(real=audio, imag=tf.zeros_like(audio)), tf.complex64)
    )
    fft = tf.expand_dims(fft, axis=-1)

    # Return the absolute value of the first half of the FFT
    # which represents the positive frequencies
    return tf.math.abs(fft[:, : (32000 // 2), :])


def path_to_audio(path):
    """Reads and decodes an audio file."""
    audio = tf.io.read_file(path)
    audio, _ = tf.audio.decode_wav(audio, 1, 2 * 16000)
    return audio


def oneHotPrevActions(actions):
    oneHot = np.zeros(shape=(NUM_ACTION_HISTORY, N_DISCRETE_ACTIONS, 1))
    for i in range(NUM_ACTION_HISTORY):
        if len(actions) >= (i + 1):
            oneHot[i][actions[-(i + 1)]][0] = 1
    return oneHot


def take_action(action):
    action = int(action)
    #update_status(f'Custom action: {action}')
    if action == 0:
        elden_agent_keyboard.release('w')
        elden_agent_keyboard.release('s')
        elden_agent_keyboard.press('w')
        #elden_agent_keyboard.tap('w')
        # self.keys_pressed.append('w')
    elif action == 1:
        elden_agent_keyboard.release('w')
        elden_agent_keyboard.release('s')
        elden_agent_keyboard.press('s')
        #elden_agent_keyboard.tap('s')
        # self.keys_pressed.append('s')
    elif action == 2:
        elden_agent_keyboard.release('a')
        elden_agent_keyboard.release('d')
        elden_agent_keyboard.press('a')
        #elden_agent_keyboard.tap('a')
        # self.keys_pressed.append('a')
    elif action == 3:
        elden_agent_keyboard.release('a')
        elden_agent_keyboard.release('d')
        elden_agent_keyboard.press('d')
        #elden_agent_keyboard.tap('d')
        # self.keys_pressed.append('d')
    elif action == 4:
        elden_agent_keyboard.release('w')
        elden_agent_keyboard.release('s')
        elden_agent_keyboard.release('a')
        elden_agent_keyboard.release('d')
        pass
    elif action == 5:
        #press_key(kb.Key.space, 0.1)
        elden_agent_keyboard.tap(kb.Key.space)
    elif action == 6:
        #press_key('4', 0.1)
        elden_agent_keyboard.tap('4')
    elif action == 7:
        # press_key(kb.Key.shift_l, 0.1)
        # press_key('4', 0.1)
        elden_agent_keyboard.press(kb.Key.shift_l)
        elden_agent_keyboard.tap('4')
        elden_agent_keyboard.release(kb.Key.shift_l)
    elif action == 8:
        #press_key('5', 0.5)
        #elden_agent_keyboard.tap('5')
        elden_agent_keyboard.tap('r')
        


class AudioRecorder():
    # Audio class based on pyAudio and Wave
    def __init__(self):
        self.open = True
        self.rate = 16000
        self.frames_per_buffer = 16000 * 2
        self.channels = 1
        self.format = pyaudio.paInt16
        self.audio_filename = "parry.wav"
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=self.format,
                                      channels=self.channels,
                                      rate=self.rate,
                                      input=True,
                                      frames_per_buffer = self.frames_per_buffer,
                                      input_device_index=19)
        self.audio_frames = []
        self.active = False


    # Audio starts being recorded
    def record(self, iter):
        self.active = True
        data = self.stream.read(self.frames_per_buffer) 
        self.audio_frames.append(data)
        file_name = os.path.join('parries', self.audio_filename[:-4] + "_" + str(iter).zfill(7) + '.wav')
        waveFile = wave.open(file_name, 'wb')
        waveFile.setnchannels(self.channels)
        waveFile.setsampwidth(self.audio.get_sample_size(self.format))
        waveFile.setframerate(self.rate)
        waveFile.writeframes(b''.join(self.audio_frames))
        waveFile.close()
        self.active = False



    def get_audio(self):
        if len(self.audio_frames) > 0:
            return self.audio_frames.pop()
        else:
            return None


    def close(self):
        self.active = False
        self.stream.close()
        self.audio.terminate()

        waveFile = wave.open(self.audio_filename, 'wb')
        waveFile.setnchannels(self.channels)
        waveFile.setsampwidth(self.audio.get_sample_size(self.format))
        waveFile.setframerate(self.rate)
        waveFile.writeframes(b''.join(self.audio_frames))
        waveFile.close()

    # Launches the audio recording function using a thread
    def start(self, iter):
        if not self.active:
            audio_thread = threading.Thread(target=self.record, args=(iter,))
            audio_thread.start()


class EldenEnv(gym.Env):
    """Custom Environment that follows gym interface"""

    def __init__(self, logdir, resume=False, stream_pc_ip=None):
        super(EldenEnv, self).__init__()
        # Define action and observation space
        # They must be gym.spaces objects
        # Example when using discrete actions:
        self.action_space = spaces.Discrete(N_DISCRETE_ACTIONS)
        # Example for using image as input (channel-first; channel-last also works):
        spaces_dict = {
            'img': spaces.Box(low=0, high=255, shape=(MODEL_HEIGHT, MODEL_WIDTH, N_CHANNELS), dtype=np.uint8),
            'prev_actions': spaces.Box(low=0, high=1, shape=(NUM_ACTION_HISTORY, N_DISCRETE_ACTIONS, 1), dtype=np.uint8),
            'state': spaces.Box(low=0, high=1, shape=(2,), dtype=np.float32),
        }
        self.observation_space = gym.spaces.Dict(spaces_dict)
        self.stream_pc_ip = stream_pc_ip
        self.agent_ip = 'localhost'
        self.logger = SummaryWriter(os.path.join(logdir, 'A2C_0'))
        
        headers = {"Content-Type": "application/json"}
        requests.post(f"http://{self.agent_ip}:6000/action/start_elden_ring", headers=headers)
        time.sleep(90)

        #requests.post(f"http://{self.agent_ip}:6000/action/stop_elden_ring", headers=headers)
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
        if not resume:
            self.num_runs = 0
        else:
            self.num_runs = 2863
        self.max_reward = None
        self.time_since_r = time.time()
        self.reward_history = []
        self.parry_dict = {'vod_duration':None,
                           'parries': []}
        self.t_since_parry = None
        self.parry_detector = tf.saved_model.load('parry_detector')
        self.prev_step_end_ts = time.time()
        self.last_fps = []
        self.sct = mss()
        self.audio_cap = AudioRecorder()
        self.boss_hp_end_history = []
        self.action_history = []
        self.time_since_restart = time.time()
        self.wasHealed = False
        if not resume:
            threading.Thread(target=timer_callback, args=(time.time(),)).start()
        else:
            with open('obs_timer.txt', 'r') as f:
                matches = re.match(r"(\d\d):(\d\d):(\d\d):(\d\d).*", f.read())
            seconds = int(matches[4])
            minutes = int(matches[3])
            hours = int(matches[2])
            days = int(matches[1])
            original_ts = time.time() - (seconds + (minutes * 60) + (hours * 60 * 60) + (days * 24 * 60* 60))
            threading.Thread(target=timer_callback, args=(original_ts,)).start()

        #subprocess.Popen(['python', 'timer.py', '>', 'obs_timer.txt'])


    def grab_screen_shot(self):
        for num, monitor in enumerate(self.sct.monitors[1:], 1):
            # Get raw pixels from the screen
            sct_img = self.sct.grab(monitor)

            # Create the Image
            #decoded = cv2.imdecode(np.frombuffer(sct_img, np.uint8), -1)
            return cv2.cvtColor(np.asarray(sct_img), cv2.COLOR_BGRA2RGB)


    def step(self, action):
        if self.first_step:
            headers = {"Content-Type": "application/json"}
            requests.post(f"http://{self.agent_ip}:6000/action/init_fight", headers=headers)
            requests.post(f"http://{self.stream_pc_ip}:6000/obs/recording/start", headers=headers)
            self.rewardGen.dmg_timer = time.time()
        #print('step start')
        t0 = time.time()
        # if not self.first_step:
        #     if t0 - self.prev_step_end_ts > 5:
        #         headers = {"Content-Type": "application/json"}
        #         for i in range(4):
        #             requests.post(f"http://{self.agent_ip}:6000/action/custom/{4}", headers=headers)
        #             requests.post(f"http://{self.agent_ip}:6000/action/release_keys/{1}", headers=headers)
        #             time.sleep(1)
        #         requests.post(f"http://{self.agent_ip}:6000/action/return_to_grace", headers=headers)
        #         time.sleep(5)
        #         requests.post(f"http://{self.agent_ip}:6000/action/release_keys/{1}", headers=headers)
        #         self.done = True
        #     self.logger.add_scalar('time_between_steps', t0 - self.prev_step_end_ts, self.iteration)

        parry_reward = 0
        # if int(action) == 9:
        #     self.audio_cap.start(self.iteration)
        #     self.parry_dict['parries'].append(time.time() - self.t_start)
        # if int(action) == 9:
        #     if self.t_since_parry is None or (time.time() - self.t_since_parry) > 2.1:
        #         headers = {"Content-Type": "application/json"}
        #         requests.post(f"http://{self.agent_ip}:6000/recording/start", headers=headers)
        #         self.t_since_parry = time.time()
        # if not self.t_since_parry is None and (time.time() - self.t_since_parry) > 2:
        #     headers = {"Content-Type": "application/json"}
        #     response = requests.post(f"http://{self.agent_ip}:6000/recording/stop", headers=headers)
        # headers = {"Content-Type": "application/json"}
        # response = requests.post(f"http://{self.agent_ip}:6000/recording/get_num_files", headers=headers)
        # if response.json()['num_files'] > 0:
        #     try:
        #         response = requests.post(f"http://{self.agent_ip}:6000/recording/get_parry", headers=headers)
        #         print(response.json())
        #         parry_sound_bytes = response.json()['parry_sound_bytes']
        #         decoded_bytes = base64.b64decode(parry_sound_bytes)
        #         byte_io = io.BytesIO(decoded_bytes)
        #         AudioSegment.from_raw(byte_io, 16000*2, 16000, 1).export(f'parries/{self.iteration}.wav', format='wav')
        #         audio = np.expand_dims(byte_io, axis=0)
        #         fft = audio_to_fft(audio)
        #         y_pred = self.parry_detector(fft)
        #         labels = np.squeeze(y_pred)
        #         index = np.argmax(labels, axis=0)
        #         if CLASS_NAMES[index] == 'successful_parries':
        #             parry_reward = 1
        #     except Exception as e:
        #         print(str(e))
        #print('focus window')
        t1 = time.time()

        #print('release keys')
        headers = {"Content-Type": "application/json"}
        #requests.post(f"http://{self.agent_ip}:6000/action/release_keys", headers=headers)

        frame = self.grab_screen_shot()
        #print('reward update')
        t2 = time.time()
        time_alive, percent_through, hp, self.death, dmg_reward, find_reward, time_since_boss_seen, since_taken_dmg_reward, dodge_reward, no_dmg_reward = self.rewardGen.update(frame)

        # audio_buffer = self.audio_cap.get_audio()
        # if not audio_buffer is None:
        #     audio_input = np.expand_dims(np.frombuffer(audio_buffer, dtype=np.int16), axis=-1)
        #     audio_input = np.expand_dims(audio_input, axis=0)
        #     audio_input = audio_input.astype(np.float32)
        #     #print(audio_input.shape)
        #     fft = audio_to_fft(audio_input)
        #     pred = self.parry_detector(fft)
        #     pred = np.squeeze(pred)
        #     pred_idx = np.argmax(pred, axis=0)
        #     #print(pred_idx)
        #     if CLASS_NAMES[int(pred_idx)] == 'successful_parries' and pred[int(pred_idx)] > 0.99:
        #         parry_reward = 1

        t3 = time.time()
        self.logger.add_scalar('time_alive', time_alive, self.iteration)
        self.logger.add_scalar('percent_through', percent_through, self.iteration)
        self.logger.add_scalar('hp', hp, self.iteration)
        self.logger.add_scalar('dmg_reward', dmg_reward, self.iteration)
        self.logger.add_scalar('find_reward', find_reward, self.iteration)
        self.logger.add_scalar('parry_reward', parry_reward, self.iteration)
        self.logger.add_scalar('since_taken_dmg_reward', since_taken_dmg_reward, self.iteration)
        self.logger.add_scalar('dodge_reward', dodge_reward, self.iteration)
        self.logger.add_scalar('no_dmg_reward', no_dmg_reward, self.iteration)
        self.reward = hp + dmg_reward + no_dmg_reward # + dodge_reward #  + since_taken_dmg_reward # + parry_reward # time_alive + percent_through find_reward + 

        # if int(action) == 5 and self.rewardGen.time_since_dodge is None:
        #     self.rewardGen.taken_dmg_during_dodge = False
        #     self.rewardGen.time_since_dodge = time.time()

        # if int(action) == 5 and self.rewardGen.time_since_dodge is None:
        #     self.rewardGen.taken_dmg_during_dodge = False
        #     self.rewardGen.time_since_dodge = time.time()

        #print('custom action')
        if not self.death and not self.done:
            # Time limit for fighting Tree sentienel (600 seconds or 10 minutes)
            if (time.time() - self.t_start) > 30 and not self.rewardGen.seen_boss:
                headers = {"Content-Type": "application/json"}
                for i in range(5):
                    take_action(4)
                    #requests.post(f"http://{self.agent_ip}:6000/action/release_keys/{1}", headers=headers)
                    time.sleep(1)
                requests.post(f"http://{self.stream_pc_ip}:6000/obs/recording/stop", headers=headers)
                #requests.post(f"http://{self.agent_ip}:6000/action/release_keys/{1}", headers=headers)
                requests.post(f"http://{self.agent_ip}:6000/action/return_to_grace", headers=headers)
                self.done = True
                self.reward = -1
                self.rewardGen.time_since_death = time.time()
            else:
                if int(action) == 8:
                    self.time_since_r = time.time()
                take_action(action)
                
                self.consecutive_deaths = 0
        else:
            headers = {"Content-Type": "application/json"}
            # if we load in and die with 5 seconds, restart game because we are frozen on a black screen
            if self.first_step:
                self.consecutive_deaths += 1
                if self.consecutive_deaths > 5:
                    self.consecutive_deaths = 0
                    requests.post(f"http://{self.stream_pc_ip}:6000/obs/recording/stop", headers=headers)
                    headers = {"Content-Type": "application/json"}
                    requests.post(f"http://{self.agent_ip}:6000/action/stop_elden_ring", headers=headers)
                    time.sleep(5 * 60)
                    headers = {"Content-Type": "application/json"}
                    requests.post(f"http://{self.agent_ip}:6000/action/start_elden_ring", headers=headers)
                    time.sleep(180)

                    headers = {"Content-Type": "application/json"}
                    requests.post(f"http://{self.agent_ip}:6000/action/load_save", headers=headers)

                    headers = {"Content-Type": "application/json"}
                    requests.post(f"http://{self.agent_ip}:6000/action/return_to_grace", headers=headers)
                    self.time_since_restart = time.time()
            else:
                headers = {"Content-Type": "application/json"}
                #requests.post(f"http://{self.agent_ip}:6000/recording/stop", headers=headers)
                requests.post(f"http://{self.agent_ip}:6000/action/death_reset", headers=headers)
                for i in range(5):
                    take_action(4)
                    #requests.post(f"http://{self.agent_ip}:6000/action/custom/{4}", headers=headers)
                    #requests.post(f"http://{self.agent_ip}:6000/action/release_keys/{1}", headers=headers)
                    time.sleep(1)
                requests.post(f"http://{self.stream_pc_ip}:6000/obs/recording/stop", headers=headers)
            self.done = True
        #print('final steps')
        t4 = time.time()
        observation = cv2.resize(frame, (MODEL_WIDTH, MODEL_HEIGHT))
        info = {}
        self.first_step = False
        self.iteration += 1

        # if self.reward < -1:
        #     self.reward = -1
        # if self.reward > 1:
        #     self.reward = 1

        if self.max_reward is None:
            self.max_reward = self.reward
        elif self.max_reward < self.reward:
            self.max_reward = self.reward

        self.logger.add_scalar('reward', self.reward, self.iteration)
        self.reward_history.append(self.reward)

        t_end = time.time()
        # print("Iteration: {} took {:.2f} seconds".format(self.iteration, t_end - t0))
        # print("t0-t1 took {:.5f} seconds".format(t1 - t0))
        # print("t1-t2 took {:.5f} seconds".format(t2 - t1))
        # print("t2-t3 took {:.5f} seconds".format(t3 - t2))
        # print("t3-t4 took {:.5f} seconds".format(t4 - t3))
        # print("t4-t_end took {:.5f} seconds".format(t_end - t4))
        self.last_fps.append(1 / (t_end - t0))
        desired_fps = (1 / 15) 
        time_to_sleep = desired_fps - (t_end - t0)
        #print(1 / (time.time() - t0))
        if time_to_sleep > 0:
            time.sleep(time_to_sleep)
        self.logger.add_scalar('step_time', (time.time() - t0), self.iteration)
        self.logger.add_scalar('FPS', 1 / (time.time() - t0), self.iteration)
        self.prev_step_end_ts = time.time()
        spaces_dict = {
            'img': observation,
            'prev_actions': oneHotPrevActions(self.action_history),
            'state': np.asarray([self.rewardGen.curr_hp, self.rewardGen.curr_stam])
        }
        self.action_history.append(int(action))
        if (self.iteration % HORIZON_WINDOW) == 0:
            headers = {"Content-Type": "application/json"}
            for i in range(5):
                take_action(4)
                #requests.post(f"http://{self.agent_ip}:6000/action/custom/{4}", headers=headers)
                #requests.post(f"http://{self.agent_ip}:6000/action/release_keys/{1}", headers=headers)
                time.sleep(1)
            #requests.post(f"http://{self.agent_ip}:6000/action/release_keys/{1}", headers=headers)
            requests.post(f"http://{self.agent_ip}:6000/action/return_to_grace", headers=headers)
            json_message = {'text': 'Collecting rollout buffer'}
            headers = {"Content-Type": "application/json"}
            requests.post(f"http://{self.agent_ip}:6000/status/update", headers=headers, data=json.dumps(json_message))
            self.done = True
            self.rewardGen.time_since_death = time.time()
        return spaces_dict, self.reward, self.done, info
    
    def reset(self):
        self.done = False
        #self.cap = ThreadedCamera('/dev/video0')
        headers = {"Content-Type": "application/json"}
        #requests.post(f"http://{self.agent_ip}:6000/action/release_keys/{1}", headers=headers)
        #requests.post(f"http://{self.agent_ip}:6000/action/custom/{4}", headers=headers)
        self.num_runs += 1
        self.logger.add_scalar('iteration_finder', self.iteration, self.num_runs)

        self.parry_dict['vod_duration'] = time.time() - self.t_start

        json_message = {'text': 'Check for frozen screen'}
        headers = {"Content-Type": "application/json"}
        requests.post(f"http://{self.agent_ip}:6000/status/update", headers=headers, data=json.dumps(json_message))
        self.action_history = []
        avg_fps = 0
        for i in range(len(self.last_fps)):
            avg_fps += self.last_fps[i]
        if len(self.last_fps) > 0:
            avg_fps = avg_fps / len(self.last_fps)
        self.last_fps = []
        #requests.post(f"http://{self.agent_ip}:6000/action/death_reset", headers=headers)
        self.boss_hp_end_history.append(self.rewardGen.boss_hp)
        avg_boss_hp = 0
        if len(self.boss_hp_end_history) > 0:
            for i in range(len(self.boss_hp_end_history)):
                avg_boss_hp += self.boss_hp_end_history[i]
            avg_boss_hp /= len(self.boss_hp_end_history)
        json_message = {"death": self.death,
                        "reward": avg_fps,
                        "num_run": self.num_runs,
                        "lowest_boss_hp": avg_boss_hp}

        requests.post(f"http://{self.stream_pc_ip}:6000/obs/log/attempt_update", headers=headers, data=json.dumps(json_message))

        frame = self.grab_screen_shot()
        # next_text_image = frame[1015:1040, 155:205]
        # next_text_image = cv2.resize(next_text_image, ((205-155)*3, (1040-1015)*3))
        # next_text = pytesseract.image_to_string(next_text_image,  lang='eng',config='--psm 6 --oem 3')
        # loading_screen = "Next" in next_text
        loading_screen_history = []
        max_loading_screen_len = 30 * 15
        time.sleep(2)
        #requests.post(f"http://{self.agent_ip}:6000/action/release_keys", headers=headers)
        #requests.post(f"http://{self.agent_ip}:6000/action/custom/{4}", headers=headers)
        t_check_frozen_start = time.time()
        t_since_seen_next = None
        num_next = 0
        while True:
            frame = self.grab_screen_shot()
            next_text_image = frame[1015:1040, 155:205]
            next_text_image = cv2.resize(next_text_image, ((205-155)*3, (1040-1015)*3))
            next_text = pytesseract.image_to_string(next_text_image,  lang='eng',config='--psm 6 --oem 3')

            lower = np.array([0,0,75])
            upper = np.array([255,255,255])
            hsv = cv2.cvtColor(next_text_image, cv2.COLOR_RGB2HSV)
            mask = cv2.inRange(hsv, lower, upper)
            matches = np.argwhere(mask==255)
            percent_match = len(matches) / (mask.shape[0] * mask.shape[1])
            #print(percent_match)
            next_text = pytesseract.image_to_string(mask,  lang='eng',config='--psm 6 --oem 3')
            loading_screen = "Next" in next_text or "next" in next_text
            if loading_screen:
                print("Loading Screen:", loading_screen)
                t_since_seen_next = time.time()
                num_next += 1
            else:
                frame = self.grab_screen_shot()
                hp_image = frame[51:55, 155:155 + int(self.rewardGen.max_hp * self.rewardGen.hp_ratio) - 20]
                lower = np.array([0,150,75])
                upper = np.array([150,255,125])
                hsv = cv2.cvtColor(hp_image, cv2.COLOR_RGB2HSV)
                mask = cv2.inRange(hsv, lower, upper)
                matches = np.argwhere(mask==255)
                curr_hp = len(matches) / (hp_image.shape[1] * hp_image.shape[0])
                print(curr_hp)
                if curr_hp < 0.75:
                    print("Can't see health")
                    t_since_seen_next = time.time()
                    num_next += 1
            # elif abs(percent_match - 0.23) < 0.02:
            #     print(percent_match)
            #     t_since_seen_next = time.time()
            #     num_next += 1
            if not t_since_seen_next is None and ((time.time() - t_check_frozen_start) > 7.5) and (time.time() - t_since_seen_next) > 2.5:
                break
            elif not t_since_seen_next is None and  ((time.time() - t_check_frozen_start) > 60):
                break
            elif t_since_seen_next is None and ((time.time() - t_check_frozen_start) > 20):
                break
        self.logger.add_scalar('check_frozen_time', time.time() - t_check_frozen_start, self.num_runs)
        self.logger.add_scalar('num_next', num_next, self.num_runs)

        # # This didnt work :(
        # lost_connection_image = frame[475:550, 675:1250]
        # lost_connection_image = cv2.resize(lost_connection_image, ((1250-675)*3, (550-475)*3))
        # lost_connection_text = pytesseract.image_to_string(lost_connection_image,  lang='eng',config='--psm 6 --oem 3')
        # lost_connection_words = ["connection", "game", "server", "lost"]
        lost_connection = False
        # for word in lost_connection_words:
        #     if word in lost_connection_text:
        #         lost_connection = True
        
        hasCrashed = False
        for i in range(5):
            headers = {"Content-Type": "application/json"}
            response = requests.post(f"http://{self.agent_ip}:6000/action/check_er", headers=headers)
            print(response.json())
            if response.json()['ER']:
                hasCrashed = True
            time.sleep(0.5)
        #print(hasCrashed)

        if ((not t_since_seen_next is None) and ((time.time() - t_check_frozen_start) > 59)) or lost_connection or (hasCrashed) or (num_next > 60):
            print(f"Lost connection: {lost_connection}")
            print(f"Loading Screen Length: {len(loading_screen_history)}")
            print(f"Check ER: {not response.json()['ER']}")
            headers = {"Content-Type": "application/json"}
            still_running = False
            for i in range(5):
                frame = self.grab_screen_shot()
                parry_image = frame[680:705, 80:150]
                parry_image = cv2.resize(parry_image, (parry_image.shape[1]*3, parry_image.shape[0]*3))

                lower = np.array([0,0,75])
                upper = np.array([255,255,255])
                hsv = cv2.cvtColor(parry_image, cv2.COLOR_RGB2HSV)
                mask = cv2.inRange(hsv, lower, upper)
                matches = np.argwhere(mask==255)
                percent_match = len(matches) / (mask.shape[0] * mask.shape[1])
                next_text = pytesseract.image_to_string(mask,  lang='eng',config='--psm 6 --oem 3')
                loading_screen = "Parry" in next_text or "parry" in next_text
                if loading_screen or abs(percent_match - 0.19) < 0.02:
                    still_running = True
            if still_running or (not hasCrashed):
                requests.post(f"http://{self.agent_ip}:6000/action/stop_elden_ring", headers=headers)
            time.sleep(5 * 60)
            headers = {"Content-Type": "application/json"}
            requests.post(f"http://{self.agent_ip}:6000/action/start_elden_ring", headers=headers)
            time.sleep(180)

            headers = {"Content-Type": "application/json"}
            requests.post(f"http://{self.agent_ip}:6000/action/load_save", headers=headers)
            self.time_since_restart = time.time()


        #headers = {"Content-Type": "application/json"}
        #requests.post(f"http://{self.agent_ip}:6000/recording/tag_latest/{self.max_reward}/{self.num_runs}'", headers=headers, data=json.dumps(self.parry_dict))

        observation = cv2.resize(frame, (MODEL_WIDTH, MODEL_HEIGHT))
        spaces_dict = {
            'img': observation,
            'prev_actions': oneHotPrevActions(self.action_history),
            'state': np.asarray([1.0, 1.0])
        }
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
        self.rewardGen.time_since_dmg_healed = time.time()
        self.rewardGen.hits_taken = 0
        self.rewardGen.total_dmg_taken = 0
        
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

        self.t_start = time.time()
        headers = {"Content-Type": "application/json"}
        #requests.post(f"http://{self.agent_ip}:6000/recording/start", headers=headers)
        if (self.iteration % HORIZON_WINDOW) == 0:
            json_message = {'text': 'Training model'}
            headers = {"Content-Type": "application/json"}
            requests.post(f"http://{self.agent_ip}:6000/status/update", headers=headers, data=json.dumps(json_message))
            #time.sleep(120)
        time.sleep(0.5)
        headers = {"Content-Type": "application/json"}
        #requests.post(f"http://{self.agent_ip}:6000/action/release_keys", headers=headers)
        #requests.post(f"http://{self.agent_ip}:6000/action/custom/{4}", headers=headers)

        json_message = {'text': 'Step'}
        headers = {"Content-Type": "application/json"}
        requests.post(f"http://{self.agent_ip}:6000/status/update", headers=headers, data=json.dumps(json_message))
        self.rewardGen.time_since_taken_dmg = time.time()
        return spaces_dict

    def render(self, mode='human'):
        pass

    def close (self):
        self.cap.release()





