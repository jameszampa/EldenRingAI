import os
import re
import json
import time
import time
import secrets
import win32gui
import subprocess
from pynput import keyboard as kb
from flask import Flask, request, Response


class WindowMgr:
    """Encapsulates some calls to the winapi for window management"""

    def __init__ (self):
        """Constructor"""
        self._handle = None

    def find_window(self, class_name, window_name=None):
        """find a window by its class_name"""
        self._handle = win32gui.FindWindow(class_name, window_name)

    def _window_enum_callback(self, hwnd, wildcard):
        """Pass to win32gui.EnumWindows() to check all the opened windows"""
        if re.match(wildcard, str(win32gui.GetWindowText(hwnd))) is not None:
            self._handle = hwnd

    def find_window_wildcard(self, wildcard):
        """find a window whose title matches the wildcard regex"""
        self._handle = None
        win32gui.EnumWindows(self._window_enum_callback, wildcard)

    def set_foreground(self):
        """put the window in the foreground"""
        win32gui.SetForegroundWindow(self._handle)

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
            try:
                elden_agent.w = WindowMgr()
                elden_agent.w.find_window_wildcard('ELDEN RING.*')
                elden_agent.w.set_foreground()
            except Exception as e:
                time.sleep(60 * 3)
                os.system("taskkill /f /im eldenring.exe")
                time.sleep(60 * 5)
                subprocess.run([elden_agent.path_elden_ring])
                time.sleep(180)
                elden_agent.keyboard.release('w')
                elden_agent.keyboard.release('s')
                elden_agent.keyboard.release('a')
                elden_agent.keyboard.release('d')

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
            elden_agent.keys_pressed = []
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
            action = int(action)
            if action == 0:
                elden_agent.keyboard.release('w')
                elden_agent.keyboard.release('s')
                elden_agent.keyboard.press('w')
            elif action == 1:
                elden_agent.keyboard.release('w')
                elden_agent.keyboard.release('s')
                elden_agent.keyboard.press('s')
            elif action == 2:
                elden_agent.keyboard.release('a')
                elden_agent.keyboard.release('d')
                elden_agent.keyboard.press('a')
            elif action == 3:
                elden_agent.keyboard.release('a')
                elden_agent.keyboard.release('d')
                elden_agent.keyboard.press('d')
            elif action == 4:
                elden_agent.keyboard.release('w')
                elden_agent.keyboard.release('s')
                elden_agent.keyboard.release('a')
                elden_agent.keyboard.release('d')
            elif action == 5:
                press_key(kb.Key.space, 0.1)
            elif action == 6:
                press_key('4', 0.1)
            elif action == 7:
                press_key(kb.Key.shift_l, 0.1)
                press_key('4', 0.1)
            elif action == 8:
                press_key('5', 0.5)
            elif action == 9:
                press_key(kb.Key.shift_l, 0.1)
                press_key('5', 0.1)
            elif action == 10:
                press_key('r', 0.1)
            elif action == 11:
                press_key(kb.Key.space, 0.5)
            elif action == 12:
                press_key('f', 0.1)
            return Response(status=200)
        except Exception as e:
            return json.dumps({'error':str(e)})
    else:
        return Response(status=400)


@app.route('/action/return_to_grace', methods=["POST"])
def return_to_grace():
    if request.method == 'POST':
        try:
            elden_agent.keyboard.release('w')
            elden_agent.keyboard.release('s')
            elden_agent.keyboard.release('a')
            elden_agent.keyboard.release('d')
            time.sleep(1)
            elden_agent.keyboard.press('e')
            elden_agent.keyboard.press('3')
            time.sleep(0.1)
            elden_agent.keyboard.release('e')
            elden_agent.keyboard.release('3')
            time.sleep(1)
            elden_agent.keyboard.press(kb.Key.left)
            time.sleep(0.1)
            elden_agent.keyboard.release(kb.Key.left)
            time.sleep(1)
            elden_agent.keyboard.press('e')
            time.sleep(0.1)
            elden_agent.keyboard.release('e')
            time.sleep(11)
            return Response(status=200)
        except Exception as e:
            return json.dumps({'error':str(e)})
    else:
        return Response(status=400)


@app.route('/action/init_fight', methods=["POST"])
def init_fight():
    if request.method == 'POST':
        try:
            elden_agent.keyboard.press('w')
            elden_agent.keyboard.press(kb.Key.space)
            time.sleep(2.35)
            elden_agent.keyboard.press('f')
            time.sleep(0.05)
            elden_agent.keyboard.release('f')
            time.sleep(4)
            elden_agent.keyboard.press('d')
            time.sleep(1)
            elden_agent.keyboard.release('d')
            time.sleep(2.5)
            elden_agent.keyboard.press('a')
            time.sleep(1)
            elden_agent.keyboard.release('a')
            time.sleep(1.5)
            elden_agent.keyboard.release('w')
            elden_agent.keyboard.release(kb.Key.space)
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
            for key in elden_agent.keys_pressed:
                if type(key) == str:
                    elden_agent.keyboard.release(key)
                    elden_agent.keys_pressed.remove(key)
                else:
                    if time.time() - key[2] > key[1]:
                        elden_agent.keyboard.release(key[0])
                        elden_agent.keys_pressed.remove(key)
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
            stats = _get_stats(int(char_slot))
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