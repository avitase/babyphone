#!/usr/bin/env python

import functools
import logging
import os
import signal
import time
from importlib import import_module
from threading import Thread

from flask import Flask, render_template, Response

from camera_proxy import CameraProxy

# import camera driver
if os.environ.get('CAMERA'):
    Camera = import_module('camera_' + os.environ['CAMERA']).Camera
else:
    from camera_test import Camera

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
    default_socket = 'ipc:///tmp/camera.socket'

    camera_proxy = CameraProxy(socket=app.config.get('CAMERA_SOCKET', default_socket))
    return Response(generate_frame(camera=camera_proxy,
                                   fps=app.config.get('FPS', default_FPS)),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


def start_camera_thread():
    default_socket = 'ipc:///tmp/camera.socket'
    camera = Camera(socket=app.config.get('CAMERA_SOCKET', default_socket))
    thread = Thread(target=camera.run)

    app.logger.info('Starting camera thread')
    thread.start()
    return camera, thread


def exit_gracefully(signum, frame, camera, thread):
    camera.stop()
    thread.join()


if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

    camera, thread = start_camera_thread()

    do_exit = functools.partial(exit_gracefully, camera=camera, thread=thread)
    signal.signal(signal.SIGINT, do_exit)
    signal.signal(signal.SIGTERM, do_exit)

if __name__ == '__main__':
    camera, thread = start_camera_thread()

    app.run(host='0.0.0.0', threaded=True)

    camera.stop()
    thread.join()
