import datetime
import io
import time

import picamera

from base_camera import BaseCamera


class Camera(BaseCamera):
    def __init__(self, socket):
        super(Camera, self).__init__(socket)

        self._camera = picamera.PiCamera()
        self._camera.resolution = (640, 480)
        self._camera.rotation = 180
        self._camera.annotate_background = picamera.Color('black')

        # give camera 2 seconds to configure
        time.sleep(2)

    def next_frame(self):
        stream = io.BytesIO()
        for _ in self._camera.capture_continuous(stream, 'jpeg', use_video_port=True):
            # update timestamp
            self._camera.annotate_text = datetime.datetime.now().strftime('%H:%M:%S')

            # return current frame
            stream.seek(0)
            yield stream.read()

            # reset stream for next frame
            stream.seek(0)
            stream.truncate()
