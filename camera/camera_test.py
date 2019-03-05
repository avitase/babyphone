import io

import numpy as np
from PIL import Image

from base_camera import BaseCamera


class Camera(BaseCamera):
    def __init__(self, socket, max_fps):
        super(Camera, self).__init__(socket, max_fps)

    def rnd_img(width, height):
        vec = np.repeat(np.random.rand(width * height) * 255, 3)
        return vec.reshape((width, height, 3))


    def next_frame(self):
        pxl = Camera.rnd_img(64, 48)
        img = Image.fromarray(pxl.astype('uint8')).convert('RGB')
        img = img.resize((640, 480))

        raw = io.BytesIO()
        img.save(raw, format='jpeg')
        return raw.getvalue()
