import os
import re
import json
import time
import wave
import time
import base64
import random
import shutil
import secrets
import hashlib
import datetime
import binascii
import subprocess
import moviepy.editor as mp
from pydub import AudioSegment
from pynput import keyboard as kb
from WindowManager import WindowMgr
from flask import Flask, request, Response


def l_endian(val):
    """Takes bytes and returns little endian int32/64"""
    l_hex = bytearray(val)
    l_hex.reverse()
    str_l = "".join(format(i, "02x") for i in l_hex)
    return int(str_l, 16)


def get_slot_ls(file):
    with open(file, "rb") as fh:
        dat = fh.read()

        slot1 = dat[0x00000310 : 0x0028030F + 1]  # SLOT 1
        slot2 = dat[0x00280320 : 0x050031F + 1]
        slot3 = dat[0x500330 : 0x78032F + 1]
        slot4 = dat[0x780340 : 0xA0033F + 1]
        slot5 = dat[0xA00350 : 0xC8034F + 1]
        slot6 = dat[0xC80360 : 0xF0035F + 1]
        slot7 = dat[0xF00370 : 0x118036F + 1]
        slot8 = dat[0x1180380 : 0x140037F + 1]
        slot9 = dat[0x1400390 : 0x168038F + 1]
        slot10 = dat[0x16803A0 : 0x190039F + 1]
        return [slot1, slot2, slot3, slot4, slot5, slot6, slot7, slot8, slot9, slot10]


def get_stats(file, char_slot):
    """"""
    # print(file, char_slot)
    lvls = get_levels(file)
    lv = lvls[char_slot - 1]
    slots = get_slot_ls(file)

    start_ind = 0
    slot1 = slots[char_slot - 1]
    indexes = []
    for ind, b in enumerate(slot1):
        if ind > 60000:
            return None
        try:
            stats = [
                l_endian(slot1[ind : ind + 1]),
                l_endian(slot1[ind + 4 : ind + 5]),
                l_endian(slot1[ind + 8 : ind + 9]),
                l_endian(slot1[ind + 12 : ind + 13]),
                l_endian(slot1[ind + 16 : ind + 17]),
                l_endian(slot1[ind + 20 : ind + 21]),
                l_endian(slot1[ind + 24 : ind + 25]),
                l_endian(slot1[ind + 28 : ind + 29]),
            ]
            hp = l_endian(slot1[ind - 44 : ind - 40])

            if sum(stats) == lv + 79 and l_endian(slot1[ind + 44 : ind + 46]) == lv:
                start_ind = ind
                lvl_ind = ind + 44
                break

        except:
            continue

    idx = ind
    for i in range(8):
        indexes.append(idx)
        idx += 4

    indexes.append(lvl_ind)  # Add the level location to the end o

    fp = []
    fp_inds = []
    y = start_ind - 32

    for i in range(3):
        fp.append(l_endian(slot1[y : y + 2]))
        fp_inds.append(y)
        y += 4

    hp = []
    hp_inds = []
    x = start_ind - 44

    for i in range(3):
        hp.append(l_endian(slot1[x : x + 2]))
        hp_inds.append(x)
        x += 4

    stam = []
    stam_inds = []
    z = start_ind - 16

    for i in range(3):
        stam.append(l_endian(slot1[z : z + 2]))
        stam_inds.append(z)
        z += 4

    return [
        stats,
        indexes,
        hp_inds,
        stam_inds,
        fp_inds,
    ]


def get_levels(file):
    with open(file, "rb") as fh:
        dat = fh.read()

    ind = 0x1901D0E + 34
    lvls = []
    for i in range(10):
        l = dat[ind : ind + 2]

        lvls.append(l_endian(l))
        ind += 588
    return lvls


def _get_stats(char_slot):
    stats = get_stats(r"C:/Users/James Zampa/AppData/Roaming/EldenRing/76561199402743988/ER0000.sl2", char_slot)
    return stats[0]


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