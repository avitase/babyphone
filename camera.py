import os
import time

from base_camera import BaseCamera


class Camera(BaseCamera):
    """An emulated camera implementation that streams a repeated sequence of
    files 1.jpg, 2.jpg and 3.jpg at a rate of one frame per second."""
    file_names = [os.path.join('img', f) + '.jpg' for f in map(str, [1, 2, 3])]
    imgs = [open(f, 'rb').read() for f in file_names]

    @staticmethod
    def frames():
        while True:
            yield Camera.imgs[int(time.time()) % len(Camera.file_names)]
