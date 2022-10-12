import os
import json
import time
import secrets
import subprocess
from get_levels import get_stats
from pynput import keyboard as kb
from WindowManager import WindowMgr
from flask import Flask, request, Response


class EldenAgent:
    def __init__(self) -> None:
        self.keys_pressed = []
        self.keyboard = kb.Controller()
        self.path_elden_ring = 'C:\\Program Files (x86)\\Steam\\steamapps\\common\\ELDEN RING\\Game\\eldenring.exe'


app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_urlsafe(16)
elden_agent = EldenAgent()


@app.route('/action/focus_window', methods=["POST"])
def focus_window():
    if request.method == 'POST':
        try:
            print('FOCUS WINDOW(Do Nothing)')
            try:
                elden_agent.w = WindowMgr()
                elden_agent.w.find_window_wildcard('ELDEN RING.*')
                elden_agent.w.set_foreground()
            except Exception as e:
                print("ERROR: Could not fild Elden Ring Restarting")
                time.sleep(180)
                os.system("taskkill /f /im eldenring.exe")
                time.sleep(180)
                subprocess.run([elden_agent.path_elden_ring])
                time.sleep(180)
                elden_agent.keyboard.release('w')
                elden_agent.keyboard.release('s')
                elden_agent.keyboard.release('a')
                elden_agent.keyboard.release('d')

                time.sleep(1)

                elden_agent.keyboard.press('e')
                elden_agent.keyboard.press('4')
                time.sleep(0.1)
                elden_agent.keyboard.release('e')
                elden_agent.keyboard.release('4')

                time.sleep(1)

                elden_agent.keyboard.press(kb.Key.left)
                time.sleep(0.1)
                elden_agent.keyboard.release(kb.Key.left)

                time.sleep(1)

                elden_agent.keyboard.press('e')
                time.sleep(0.1)
                elden_agent.keyboard.release('e')

                time.sleep(30)
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


@app.route('/action/load_save', methods=["POST"])
def load_save():
    if request.method == 'POST':
        try:
            print('LOAD SAVE')
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
            print('DEATH RESET')
            elden_agent.keyboard.release('w')
            elden_agent.keyboard.release('s')
            elden_agent.keyboard.release('a')
            elden_agent.keyboard.release('d')
            time.sleep(30)
            elden_agent.keyboard.press('w')
            time.sleep(10)
            elden_agent.keyboard.release('w')
            elden_agent.keyboard.press('d')
            time.sleep(2)
            elden_agent.keyboard.release('d')
            elden_agent.keyboard.press('w')
            time.sleep(5)
            elden_agent.keyboard.release('w')
            elden_agent.keyboard.press('a')
            time.sleep(1)
            elden_agent.keyboard.release('a')
            elden_agent.keyboard.press('w')
            time.sleep(1)
            elden_agent.keyboard.release('w')
            return Response(status=200)
        except Exception as e:
            return json.dumps({'error':str(e)})
    else:
        return Response(status=400)


@app.route('/action/custom/<action>', methods=["POST"])
def custom_action(action):
    if request.method == 'POST':
        try:
            print('CUSTOM ACTION')
            action = int(action)
            if action == 0:
                elden_agent.keyboard.release('w')
                elden_agent.keyboard.release('s')
                elden_agent.keyboard.press('w')
                # self.keys_pressed.append('w')
            elif action == 1:
                elden_agent.keyboard.release('w')
                elden_agent.keyboard.release('s')
                elden_agent.keyboard.press('s')
                # self.keys_pressed.append('s')
            elif action == 2:
                elden_agent.keyboard.release('a')
                elden_agent.keyboard.release('d')
                elden_agent.keyboard.press('a')
                # self.keys_pressed.append('a')
            elif action == 3:
                elden_agent.keyboard.release('a')
                elden_agent.keyboard.release('d')
                elden_agent.keyboard.press('d')
                # self.keys_pressed.append('d')
            elif action == 4:
                elden_agent.keyboard.release('w')
                elden_agent.keyboard.release('s')
                elden_agent.keyboard.release('a')
                elden_agent.keyboard.release('d')
            elif action == 5:
                elden_agent.keyboard.press(kb.Key.space)
                time.sleep(0.05)
                elden_agent.keyboard.release(kb.Key.space)
            elif action == 6:
                elden_agent.keyboard.press('5')
                elden_agent.keys_pressed.append('5')
            elif action == 7:
                elden_agent.keyboard.press(kb.Key.shift_l)
                elden_agent.keys_pressed.append(kb.Key.shift_l)
                elden_agent.keyboard.press('5')
                elden_agent.keys_pressed.append('5')
            elif action == 8:
                elden_agent.keyboard.press('6')
                elden_agent.keys_pressed.append('6')
                time.sleep(0.5)
            elif action == 9:
                elden_agent.keyboard.press(kb.Key.shift_l)
                elden_agent.keys_pressed.append(kb.Key.shift_l)
                elden_agent.keyboard.press('6')
                elden_agent.keys_pressed.append('6')
            elif action == 10:
                elden_agent.keyboard.press('r')
                elden_agent.keys_pressed.append('r')
            elif action == 11:
                elden_agent.keyboard.press(kb.Key.space)
                elden_agent.keys_pressed.append(kb.Key.space)
                time.sleep(0.5)
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
            elden_agent.keyboard.release('w')
            elden_agent.keyboard.release('s')
            elden_agent.keyboard.release('a')
            elden_agent.keyboard.release('d')

            time.sleep(1)

            elden_agent.keyboard.press('e')
            elden_agent.keyboard.press('4')
            time.sleep(0.1)
            elden_agent.keyboard.release('e')
            elden_agent.keyboard.release('4')

            time.sleep(1)

            elden_agent.keyboard.press(kb.Key.left)
            time.sleep(0.1)
            elden_agent.keyboard.release(kb.Key.left)

            time.sleep(1)

            elden_agent.keyboard.press('e')
            time.sleep(0.1)
            elden_agent.keyboard.release('e')

            time.sleep(32.5)
            elden_agent.keyboard.press('w')
            time.sleep(10)
            elden_agent.keyboard.release('w')
            elden_agent.keyboard.press('d')
            time.sleep(2)
            elden_agent.keyboard.release('d')
            elden_agent.keyboard.press('w')
            time.sleep(5)
            elden_agent.keyboard.release('w')
            elden_agent.keyboard.press('a')
            time.sleep(0.05)
            elden_agent.keyboard.release('a')
            return Response(status=200)
        except Exception as e:
            return json.dumps({'error':str(e)})
    else:
        return Response(status=400)


@app.route('/action/lock_on', methods=["POST"])
def lock_on():
    if request.method == 'POST':
        try:
            print('LOCK ON TOGGLE')
            elden_agent.keyboard.press('q')
            time.sleep(0.05)
            elden_agent.keyboard.release('q')
            return Response(status=200)
        except Exception as e:
            return json.dumps({'error':str(e)})
    else:
        return Response(status=400)


@app.route('/action/stop_elden_ring', methods=["POST"])
def stop_elden_ring():
    if request.method == 'POST':
        try:
            print('STOP ELDEN RING')
            os.system("taskkill /f /im eldenring.exe")
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
            subprocess.run([elden_agent.path_elden_ring])
            return Response(status=200)
        except Exception as e:
            return json.dumps({'error':str(e)})
    else:
        return Response(status=400)


@app.route('/action/release_keys', methods=["POST"])
def release_keys():
    if request.method == 'POST':
        try:
            print('RELEASE KEYS')
            for key in elden_agent.keys_pressed:
                elden_agent.keyboard.release(key)
            elden_agent.keys_pressed = []
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