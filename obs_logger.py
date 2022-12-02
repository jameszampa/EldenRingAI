import os
import json
import secrets
import re
import datetime
import shutil
import threading
import time
import pynput
from flask import Flask, request, Response

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_urlsafe(16)
keyboard = pynput.keyboard.Controller()

@app.route('/obs/log/attempt_update', methods=["POST"])
def attempt_update():
    if request.method == 'POST':
        try:
            print('Log to OBS')
            request_json = request.get_json(force=True)
            with open('obs_log.txt', 'w') as f:
                f.write(f"Attempt: {request_json['num_run']}")
            return Response(status=200)
        except Exception as e:
            return json.dumps({'error':str(e)})
    else:
        return Response(status=400)


@app.route('/obs/log/timer_update', methods=["POST"])
def timer_update():
    if request.method == 'POST':
        try:
            print('Log to OBS')
            request_json = request.get_json(force=True)
            with open('obs_timer.txt', 'w') as f:
                f.write(f"{request_json['timer']}")
            return Response(status=200)
        except Exception as e:
            return json.dumps({'error':str(e)})
    else:
        return Response(status=400)

@app.route('/status/update', methods=["POST"])
def status_update():
    if request.method == 'POST':
        try:
            print('Log to OBS')
            request_json = request.get_json(force=True)
            with open('status.txt', 'w') as f:
                f.write(f"{request_json['text']}")
            return Response(status=200)
        except Exception as e:
            return json.dumps({'error':str(e)})
    else:
        return Response(status=400)


@app.route('/obs/recording/stop', methods=["POST"])
def stop_rec():
    if request.method == 'POST':
        try:
            print('start recording')
            #keyboard.tap('-')
            return Response(status=200)
        except Exception as e:
            return json.dumps({'error':str(e)})
    else:
        return Response(status=400)


@app.route('/obs/recording/start', methods=["POST"])
def start_rec():
    if request.method == 'POST':
        try:
            print('start recording')
            #keyboard.tap('=')
            return Response(status=200)
        except Exception as e:
            return json.dumps({'error':str(e)})
    else:
        return Response(status=400)