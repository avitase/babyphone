#!/usr/bin/env python

import os
import time
from importlib import import_module

from flask import Flask, render_template, Response

# import camera driver
if os.environ.get('CAMERA'):
    Camera = import_module('camera_' + os.environ['CAMERA']).Camera
else:
    from camera import Camera

# Raspberry Pi camera module (requires picamera package)
# from camera_pi import Camera

app = Flask(__name__)

# Load settings from 'settings.py'
app.config.from_object('settings')


@app.route('/')
def index():
    return render_template('index.html')


def generate_frame(camera, fps):
    now = time.time()
    t1 = now

    while True:
        frame = camera.get_frame()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        t2 = now
        dt = 1. / float(fps) - (t2 - t1)
        if dt > 0.:
            time.sleep(dt)
        t1 = now


@app.route('/video_feed')
def video_feed():
    default_FPS = 10
    return Response(generate_frame(camera=Camera(),
                                   fps=app.config.get('FPS', default_FPS)),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)
