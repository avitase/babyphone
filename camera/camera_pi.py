import io
import time

import picamera

from base_camera import BaseCamera


class Camera(BaseCamera):
    def __init__(self, socket, max_fps):
        super(Camera, self).__init__(socket, max_fps)

        self._camera = picamera.PiCamera()
        self._camera.resolution = (640, 480)
        self._camera.rotation = 180
        self._framerate = max_fps

        # give camera 2 seconds to configure
        time.sleep(2)

        self._stream = io.BytesIO()
        self._iter = self._camera.capture_continuous(self._stream, 'jpeg', use_video_port=True)

    def next_frame(self):
        next(self._iter)

        self._stream.seek(0)
        img = self._stream.read()

        self._stream.seek(0)
        self._stream.truncate()
        return img
