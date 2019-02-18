import os
import time

from base_camera import BaseCamera


class Camera(BaseCamera):
    file_names = [os.path.join('img', f) + '.jpg' for f in map(str, [1, 2, 3])]
    imgs = [open(f, 'rb').read() for f in file_names]

    @staticmethod
    def frames():
        while True:
            yield Camera.imgs[int(time.time()) % len(Camera.file_names)]
