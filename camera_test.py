import io

import numpy as np
from PIL import Image

from base_camera import BaseCamera


class Camera(BaseCamera):
    def __init__(self, socket):
        super(Camera, self).__init__(socket)

    def next_frame(self):
        pxl = np.random.rand(64, 48, 3) * 255
        img = Image.fromarray(pxl.astype('uint8')).convert('RGB')
        img = img.resize((640, 480))

        raw = io.BytesIO()
        img.save(raw, format='jpeg')
        return raw.getvalue()
