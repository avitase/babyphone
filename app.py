#!/usr/bin/env python

import logging
import time

from flask import Flask, render_template, Response

import settings_camera
from camera_proxy import CameraProxy

app = Flask(__name__)

# Load settings from 'settings.py'
app.config.from_object('settings')


@app.route('/')
def index():
    return render_template('index.html')


def generate_frame(camera, fps):
    now = time.time
    t = now()

    while True:
        frame = camera.get_frame()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        dt = 1. / float(fps) - (now() - t)
        if dt > 0.:
            time.sleep(dt)
        t = now()


@app.route('/video_feed')
def video_feed():
    default_FPS = 10

    camera_proxy = CameraProxy(socket=settings_camera.CAMERA_SOCKET)
    return Response(generate_frame(camera=camera_proxy,
                                   fps=app.config.get('FPS', default_FPS)),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)
