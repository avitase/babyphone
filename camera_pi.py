import datetime
import io
import time

import picamera
from flask import current_app

from base_camera import BaseCamera


class Camera(BaseCamera):
    @staticmethod
    def frames():
        with picamera.PiCamera() as camera:
            camera = picamera.PiCamera()
            camera.resolution = (640, 480)
            camera.rotation = 180

            camera.annotate_background = picamera.Color('black')

            get_timestamp = datetime.datetime.now().strftime('%H:%M:%S')
            camera.annotate_text = get_timestamp

            log = current_app.logger.info
            log('Warming up camera ...')
            time.sleep(2)
            log('... done warming up camera.')

            stream = io.BytesIO()
            for _ in camera.capture_continuous(stream, 'jpeg',
                                               use_video_port=True):

                # udpate timestamp
                camera.annotate_text = get_timestamp

                # return current frame
                stream.seek(0)
                yield stream.read()

                # reset stream for next frame
                stream.seek(0)
                stream.truncate()
