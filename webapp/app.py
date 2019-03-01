#!/usr/bin/env python

import logging
import time

from flask import Flask, render_template, Response

from camera import settings
from webapp.camera_proxy import CameraProxy

app = Flask(__name__)

# Load settings from 'settings.py'
app.config.from_object('settings')


@app.route('/')
def index():
    return render_template('index.html')


def generate_frame(camera, fps):
    app.logger.debug('Generating new stream of frames')

    now = time.time
    t = now()

    while True:
        frame = camera.get_frame()
        if frame is None:
            app.logger.error('Camera proxy returned None')
        else:
            app.logger.debug('Received frame from camera proxy')
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        dt = 1. / float(fps) - (now() - t)
        if dt > 0.:
            app.logger.debug('Sleep for: {:.2f}s'.format(dt))
            time.sleep(dt)
        else:
            app.logger.warning('Video stream is throtteling: dt = {:.2f}s'.format(dt))
        t = now()


@app.route('/video_feed')
def video_feed():
    app.logger.debug('New request for /video_feed')

    default_FPS = 10

    camera_proxy = CameraProxy(socket=settings.CAMERA_SOCKET)
    return Response(generate_frame(camera=camera_proxy,
                                   fps=app.config.get('FPS', default_FPS)),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ != '__main__':
    logging.info('Starting webapp (__name__ = {})'.format(__name__))

    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

if __name__ == '__main__':
    logging.info('Starting webapp (__name__ = {})'.format(__name__))

    app.run(host='0.0.0.0', threaded=True)
