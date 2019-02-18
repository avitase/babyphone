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

            log = current_app.logger.info
            log('Warming up camera ...')
            time.sleep(2)
            log('... done warming up camera.')

            stream = io.BytesIO()
            for _ in camera.capture_continuous(stream, 'jpeg',
                                               use_video_port=True):
                # return current frame
                stream.seek(0)
                yield stream.read()

                # reset stream for next frame
                stream.seek(0)
                stream.truncate()
