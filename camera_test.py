import os
import time

from base_camera import BaseCamera


class Camera(BaseCamera):
    def __init__(self, socket):
        super(Camera, self).__init__(socket)

        file_names = [os.path.join('img', f) + '.jpg' for f in map(str, [1, 2, 3])]
        self.imgs = [open(f, 'rb').read() for f in file_names]

    def next_frame(self):
        return self.imgs[int(time.time()) % len(self.imgs)]
