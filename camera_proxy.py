import io

import zmq
from PIL import Image, ImageFont, ImageDraw
import datetime as dt


class CameraProxy(object):
    def __init__(self, socket):
        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.REQ)
        self._socket.connect(socket)
        self._font = ImageFont.truetype("/usr/share/fonts/dejavu/DejaVuSans.ttf", 16)

    def get_frame(self):
        self._socket.send_string('')

        timestamp = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        img = Image.open(io.BytesIO(self._socket.recv()))
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), timestamp, (255, 106, 0), font=self._font)

        raw = io.BytesIO()
        img.save(raw, format='jpeg')
        return raw.getvalue()
