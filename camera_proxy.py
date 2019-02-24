import collections
import datetime as dt
import io
import time

import zmq
from PIL import Image, ImageFont, ImageDraw


class CameraProxy(object):
    def __init__(self, socket):
        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.REQ)
        self._socket.connect(socket)

        self._font = ImageFont.truetype('/usr/share/fonts/dejavu/DejaVuSans.ttf', 16)

        self.last_update = time.time()
        self.fps = collections.deque(maxlen=50)

    def get_frame(self):
        self._socket.send_string('')

        now = time.time
        self.fps.append(1. / (now() - self.last_update))
        self.last_update = now()

        timestamp = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        fps_avg = sum(self.fps) / len(self.fps)

        img = Image.open(io.BytesIO(self._socket.recv()))
        draw = ImageDraw.Draw(img)
        draw.text((10, 10),
                  '{}\n{:.0f} FPS'.format(timestamp, fps_avg),
                  (255, 106, 0),
                  font=self._font)

        raw = io.BytesIO()
        img.save(raw, format='jpeg')
        return raw.getvalue()
