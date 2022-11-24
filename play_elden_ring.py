import os
import json
import time
import secrets
import subprocess

from get_levels import get_stats
from pynput import keyboard as kb
from flask import Flask, request, Response
import re
import datetime
import shutil
import moviepy.editor as mp
from pydub import AudioSegment, effects
import pyaudio
import wave
import threading
import time
import subprocess
import os
#import tensorflow as tf
import numpy as np
import wave
import base64
from PIL import ImageGrab
import cv2
import pyautogui

class EldenAgent:
    def __init__(self) -> None:
        self.keys_pressed = []
        self.keyboard = kb.Controller()
        self.path_elden_ring = 'run_er.sh'


app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_urlsafe(16)
elden_agent = EldenAgent()


def update_status(text):
    with open('status.txt', 'w') as f:
        f.write(text)


def launch_er():
    # The os.setsid() is passed in the argument preexec_fn so
    # it's run after the fork() and before  exec() to run the shell.
    subprocess.Popen('./run_er.sh', stdout=subprocess.PIPE, 
                      shell=True, preexec_fn=os.setsid)


def get_er_process_ids():
    with open("check_er.txt","wb") as out, open("check_er_stderr.txt","wb") as err:
        proc1 = subprocess.Popen(['ps', 'aux'], stdout=subprocess.PIPE)
        proc2 = subprocess.Popen(['grep', 'start_protected_game'], stdin=proc1.stdout, stdout=out, stderr=err)
    
    process_ids = []
    proc1.stdout.close() # Allow proc1 to receive a SIGPIPE if proc2 exits.
    #proc2.stdout.close()
    time.sleep(1)
    with open('check_er.txt', 'r') as f:
        for line in f.readlines():
            match = re.search(r'james +(\d+)', line)
            if not match is None:
                process_ids.append(match[1])
    print(process_ids)
    return process_ids


def stop_er():
    cmd = ['kill', '-9']
    for id in get_er_process_ids():
        print(id)
        cmd.append(id)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    out, err = p.communicate()
    for line in out.split('kill:'):
        match = re.search(r'.*No such process.*', line)
        if not match is None:
            return False
    return True



@app.route('/action/load_save', methods=["POST"])
def load_save():
    if request.method == 'POST':
        try:
            print('LOAD SAVE')
            update_status('Loading save file')
            press_q = True
            for i in range(15):
                if press_q:
                    elden_agent.keyboard.press("q")
                    time.sleep(0.05)
                    elden_agent.keyboard.release("q")
                    press_q = False
                else:
                    elden_agent.keyboard.press("e")
                    time.sleep(0.05)
                    elden_agent.keyboard.release("e")
                    press_q = True
                time.sleep(1)
            time.sleep(30)
            return Response(status=200)
        except Exception as e:
            return json.dumps({'error':str(e)})
    else:
        return Response(status=400)


@app.route('/action/death_reset', methods=["POST"])
def death_reset():
    if request.method == 'POST':
        try:
            #elden_agent.keys_pressed = []
            print('DEATH RESET')
            update_status('Death reset')
            curr_reward = None
            curr_resets = None
            with open('obs_log.txt', 'r') as f:
                for line in f.readlines():
                    reward_match = re.search("Reward: (.+)", line)
                    if not reward_match is None:
                        curr_reward = float(reward_match[1])
                    resets_match = re.search("Num resets: (.+)", line)
                    if not resets_match is None:
                        curr_resets = int(resets_match[1])
            with open('obs_log.txt', 'w') as f:
                f.write(f"Dead: {True}")
                f.write("\n")
                f.write("FPS: {:.2f}".format(curr_reward))
                f.write("\n")
                f.write(f"Num resets: {curr_resets}")

            return Response(status=200)
        except Exception as e:
            return json.dumps({'error':str(e)})
    else:
        return Response(status=400)


def press_key(key_to_press, duration):
    holding = False
    for key in elden_agent.keys_pressed:
        if type(key) != str and key[0] == key_to_press:
            key[1] += duration / 2
            holding = True
    
    if not holding:
        elden_agent.keyboard.press(key_to_press)
        elden_agent.keys_pressed.append([key_to_press, duration, time.time()])


@app.route('/action/custom/<action>', methods=["POST"])
def custom_action(action):
    if request.method == 'POST':
        try:
            print('CUSTOM ACTION')
            action = int(action)
            #update_status(f'Custom action: {action}')
            if action == 0:
                elden_agent.keyboard.release('w')
                elden_agent.keyboard.release('s')
                elden_agent.keyboard.press('w')
                #elden_agent.keyboard.tap('w')
                # self.keys_pressed.append('w')
            elif action == 1:
                elden_agent.keyboard.release('w')
                elden_agent.keyboard.release('s')
                elden_agent.keyboard.press('s')
                #elden_agent.keyboard.tap('s')
                # self.keys_pressed.append('s')
            elif action == 2:
                elden_agent.keyboard.release('a')
                elden_agent.keyboard.release('d')
                elden_agent.keyboard.press('a')
                #elden_agent.keyboard.tap('a')
                # self.keys_pressed.append('a')
            elif action == 3:
                elden_agent.keyboard.release('a')
                elden_agent.keyboard.release('d')
                elden_agent.keyboard.press('d')
                #elden_agent.keyboard.tap('d')
                # self.keys_pressed.append('d')
            elif action == 4:
                elden_agent.keyboard.release('w')
                elden_agent.keyboard.release('s')
                elden_agent.keyboard.release('a')
                elden_agent.keyboard.release('d')
                pass
            elif action == 5:
                #press_key(kb.Key.space, 0.1)
                elden_agent.keyboard.tap(kb.Key.space)
            elif action == 6:
                #press_key('4', 0.1)
                elden_agent.keyboard.tap('4')
            elif action == 7:
                # press_key(kb.Key.shift_l, 0.1)
                # press_key('4', 0.1)
                elden_agent.keyboard.press(kb.Key.shift_l)
                elden_agent.keyboard.tap('4')
                elden_agent.keyboard.release(kb.Key.shift_l)
            elif action == 8:
                #press_key('5', 0.5)
                elden_agent.keyboard.tap('5')
            elif action == 9:
                # press_key(kb.Key.shift_l, 0.1)
                # press_key('5', 0.1)
                elden_agent.keyboard.press(kb.Key.shift_l)
                elden_agent.keyboard.tap('5')
                elden_agent.keyboard.release(kb.Key.shift_l)
            elif action == 10:
                #press_key('r', 0.1)
                elden_agent.keyboard.tap('r')
            elif action == 11:
                #press_key(kb.Key.space, 0.5)
                pass
            elif action == 12:
                # press_key('f', 0.1)
                elden_agent.keyboard.tap('f')
            return Response(status=200)
        except Exception as e:
            return json.dumps({'error':str(e)})
    else:
        return Response(status=400)


@app.route('/action/return_to_grace', methods=["POST"])
def return_to_grace():
    if request.method == 'POST':
        try:
            print('RETURN TO GRACE')
            update_status(f'Returning to grace')
            elden_agent.keyboard.release('w')
            elden_agent.keyboard.release('s')
            elden_agent.keyboard.release('a')
            elden_agent.keyboard.release('d')

            time.sleep(2)

            elden_agent.keyboard.press('e')
            elden_agent.keyboard.press('3')
            time.sleep(0.2)
            elden_agent.keyboard.release('e')
            elden_agent.keyboard.release('3')

            time.sleep(2)

            elden_agent.keyboard.press(kb.Key.left)
            time.sleep(0.2)
            elden_agent.keyboard.release(kb.Key.left)

            time.sleep(2)

            elden_agent.keyboard.press('e')
            time.sleep(0.2)
            elden_agent.keyboard.release('e')
            return Response(status=200)
        except Exception as e:
            return json.dumps({'error':str(e)})
    else:
        return Response(status=400)


@app.route('/action/init_fight', methods=["POST"])
def init_fight():
    if request.method == 'POST':
        try:
            print('init fight')
            update_status(f'Initializing fight')
            elden_agent.keyboard.press('w')
            elden_agent.keyboard.press(kb.Key.space)
            time.sleep(2.50)
            elden_agent.keyboard.press('f')
            time.sleep(0.05)
            elden_agent.keyboard.release('f')
            time.sleep(4)
            #elden_agent.keyboard.release(kb.Key.space)
            #elden_agent.keyboard.release('w')

            elden_agent.keyboard.press('d')
            #elden_agent.keyboard.press(kb.Key.space)
            time.sleep(1)
            elden_agent.keyboard.release('d')
            #elden_agent.keyboard.press('w')
            time.sleep(2.5)
            #elden_agent.keyboard.release('w')

            #elden_agent.keyboard.press('w')
            elden_agent.keyboard.press('a')
            time.sleep(1)
            #elden_agent.keyboard.release('w')
            elden_agent.keyboard.release('a')

            #elden_agent.keyboard.press('w')
            time.sleep(1)
            elden_agent.keyboard.release('w')
            elden_agent.keyboard.release(kb.Key.space)
            time.sleep(0.1)
            elden_agent.keyboard.press('q')
            time.sleep(0.1)
            elden_agent.keyboard.release('q')

            return Response(status=200)
        except Exception as e:
            return json.dumps({'error':str(e)})
    else:
        return Response(status=400)


@app.route('/action/check_er', methods=["POST"])
def check_er():
    if request.method == 'POST':
        try:
            print('Check er')
            ids = get_er_process_ids()
            print(ids)
            if len(ids) >= 2:
                return json.dumps({'ER':False})
            else:
                return json.dumps({'ER':True})
        except Exception as e:
            return json.dumps({'error':str(e)})
    else:
        return Response(status=400)


@app.route('/recording/start', methods=["POST"])
def start_recording():
    if request.method == 'POST':
        try:
            print('Start Recording')
            #update_status(f'Start recording')
            elden_agent.keyboard.press('=')
            time.sleep(0.05)
            elden_agent.keyboard.release('=')
            return Response(status=200)
        except Exception as e:
            return json.dumps({'error':str(e)})
    else:
        return Response(status=400)


@app.route('/recording/stop', methods=["POST"])
def stop_recording():
    if request.method == 'POST':
        try:
            print('Stop Recording')
            #update_status(f'Stop recording')
            elden_agent.keyboard.press('-')
            time.sleep(0.05)
            elden_agent.keyboard.release('-')
            #time.sleep(0.05)
            return Response(status=200)
        except Exception as e:
            return json.dumps({'error':str(e)})
    else:
        return Response(status=400)


@app.route('/recording/tag_latest/<max_reward>/<iteration>', methods=["POST"])
def tag_file(max_reward=None, iteration=None):
    if request.method == 'POST':
        try:
            print('Renaming run')
            #update_status(f'Naming recorded run #{int(iteration)}')
            request_json = request.get_json(force=True)

            max_ts = None
            file_to_rename = None
            vod_dir = r"vods"
            saved_runs_dir = r"saved_runs"
            parries_dir = r"parries"

            for file in os.listdir(vod_dir):
                file_name = file.split(".")[0]
                ts = time.mktime(datetime.datetime.strptime(file_name, "%Y-%m-%d %H-%M-%S").timetuple())
                if max_ts is None:
                    max_ts = ts
                    file_to_rename = file
                elif max_ts < ts:
                    max_ts = ts
                    file_to_rename = file
            
            source = os.path.join(vod_dir, file_to_rename)
            dest = os.path.join(saved_runs_dir, str(iteration) + "_" + str(max_reward) + '.mkv')
            shutil.move(source, dest)

            clip = mp.VideoFileClip(dest)
            clip.audio.write_audiofile(r"tmp.wav", ffmpeg_params=["-ac", "1", "-ar", "16000"])
            audio = AudioSegment.from_file(r"tmp.wav", format="wav")
            for i, parry in enumerate(request_json['parries']):
                combined = AudioSegment.empty()
                extract = audio[parry * 1000:(parry + 2) * 1000]
                combined += extract
                combined.export(os.path.join(parries_dir, str(iteration) + "_" + str(max_reward) + "_" + str(i).zfill(6) + ".wav"), format="wav")
            return Response(status=200)
        except Exception as e:
            return json.dumps({'error':str(e)})
    else:
        return Response(status=400)


@app.route('/action/stop_elden_ring', methods=["POST"])
def stop_elden_ring():
    if request.method == 'POST':
        try:
            print(get_er_process_ids())
            print('STOP ELDEN RING')
            update_status(f'Stop Elden Ring')
            elden_agent.keyboard.press(kb.Key.cmd)
            time.sleep(0.1)
            elden_agent.keyboard.release(kb.Key.cmd)
            time.sleep(0.5)
            pyautogui.moveTo(50, 475)
            pyautogui.click(button='right')
            pyautogui.moveTo(100, 500)
            pyautogui.click(button='left')
            pyautogui.moveTo(50, 250)
            pyautogui.click(button='left')
            time.sleep(20)
            #pyautogui.moveTo(750, 1250)
            #pyautogui.click(button='left')
            elden_agent.keyboard.press(kb.Key.enter)
            time.sleep(0.1)
            elden_agent.keyboard.release(kb.Key.enter)
            time.sleep(1)
            elden_agent.keyboard.press(kb.Key.enter)
            time.sleep(0.1)
            elden_agent.keyboard.release(kb.Key.enter)
            time.sleep(30)
            #while (len(get_er_process_ids()) > 1):
            pyautogui.moveTo(50, 250)
            time.sleep(1)
            pyautogui.click(button='right')
            time.sleep(1)
            pyautogui.moveTo(115, 495)
            time.sleep(1)
            pyautogui.click(button='left')
            try:
                if len(get_er_process_ids) > 1:
                    stop_er()
            except Exception as e:
                print(str(e))
            time.sleep(5)
            pyautogui.moveTo(50, 250)
            pyautogui.click(button='left')
            time.sleep(30)
            elden_agent.keyboard.press(kb.Key.enter)
            time.sleep(0.1)
            elden_agent.keyboard.release(kb.Key.enter)
            time.sleep(1)
            elden_agent.keyboard.press(kb.Key.enter)
            time.sleep(0.1)
            elden_agent.keyboard.release(kb.Key.enter)
            time.sleep(60)
            try:
                if len(get_er_process_ids) > 1:
                    stop_er()
            except Exception as e:
                print(str(e))
            time.sleep(60)
            pyautogui.moveTo(50, 250)
            time.sleep(1)
            pyautogui.click(button='right')
            time.sleep(1)
            pyautogui.moveTo(115, 495)
            time.sleep(1)
            pyautogui.click(button='left')
            time.sleep(5)
            return Response(status=200)
        except Exception as e:
            return json.dumps({'error':str(e)})
    else:
        return Response(status=400)


@app.route('/action/start_elden_ring', methods=["POST"])
def start_elden_ring():
    if request.method == 'POST':
        try:
            print('START ELDEN RING')
            update_status(f'Start Elden Ring')
            
            launch_er()
            time.sleep(5)
            pyautogui.moveTo(1220, 667)
            time.sleep(1)
            pyautogui.click(button='left')
            return Response(status=200)
        except Exception as e:
            return json.dumps({'error':str(e)})
    else:
        return Response(status=400)


@app.route('/action/release_keys', methods=["POST"])
@app.route('/action/release_keys/<force>', methods=["POST"])
def release_keys(force=False):
    if request.method == 'POST':
        try:
            print('RELEASE KEYS')
            #update_status(f'Release keys')
            
            for key in elden_agent.keys_pressed:
                if type(key) == str:
                    elden_agent.keyboard.release(key)
                    elden_agent.keys_pressed.remove(key)
                else:
                    if ((time.time() - key[2]) > key[1]) or force:
                        elden_agent.keyboard.release(key[0])
                        elden_agent.keys_pressed.remove(key)
            return Response(status=200)
        except Exception as e:
            return json.dumps({'error':str(e)})
    else:
        return Response(status=400)


@app.route('/status/update', methods=["POST"])
def status_update():
    if request.method == 'POST':
        try:
            request_json = request.get_json(force=True)
            update_status(f'{request_json["text"]}')
            return Response(status=200)
        except Exception as e:
            return json.dumps({'error':str(e)})
    else:
        return Response(status=400)


@app.route('/obs/log', methods=["POST"])
def log_to_obs():
    if request.method == 'POST':
        try:
            print('Log to OBS')
            request_json = request.get_json(force=True)
            with open('obs_log.txt', 'w') as f:
                #f.write(f"Dead: {request_json['death']}")
                #f.write("\n")
                #f.write("FPS: {:.2f}".format(float(request_json['reward'])))
                #f.write("\n")
                f.write(f"Num resets: {request_json['num_run']}")
            with open('lowest_boss_hp.txt', 'w') as f:
                f.write(f"{float(request_json['lowest_boss_hp'])}")
            return Response(status=200)
        except Exception as e:
            return json.dumps({'error':str(e)})
    else:
        return Response(status=400)



@app.route('/stats/<char_slot>', methods=["GET"])
def request_stats(char_slot=None):
    if char_slot is None:
        return Response(status=400)
    
    if request.method == 'GET':
        try:
            print('GET STATS')
            stats = get_stats(int(char_slot))
            json_stats = {'vigor' : stats[0],
                        'mind' : stats[1],
                        'endurance' : stats[2],
                        'strength' : stats[3],
                        'dexterity' : stats[4],
                        'intelligence' : stats[5],
                        'faith' : stats[6],
                        'arcane' : stats[7]}
            return json.dumps(json_stats)
        except Exception as e:
            return json.dumps({'error':str(e)})
    else:
        return Response(status=400)