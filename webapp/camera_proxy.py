import collections
import datetime as dt
import io
import time

import numpy as np
import uncertainties
import zmq
from PIL import Image, ImageFont, ImageDraw


class CameraProxy(object):
    def __init__(self, socket):
        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.REQ)

        timeout_in_ms = 1000
        self._socket.setsockopt(zmq.RCVTIMEO, timeout_in_ms)

        self._socket.connect(socket)

        self._font = ImageFont.truetype('/usr/share/fonts/dejavu/DejaVuSans.ttf', 16)

        self.last_update = time.time()
        self.fps = collections.deque(maxlen=50)

    def get_frame(self):
        try:
            self._socket.send_string('')
        except zmq.ZMQError:
            return None

        now = time.time
        self.fps.append(1. / (now() - self.last_update))
        self.last_update = now()

        timestamp = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        text = str(timestamp)

        if len(self.fps) == self.fps.maxlen:
            fps_avg = sum(self.fps) / len(self.fps)
            fps_std = np.sqrt(
                sum((fps - fps_avg) ** 2 for fps in self.fps)
                / (float(len(self.fps)) - 1.0)
            )


            n, s = str(uncertainties.ufloat(fps_avg, fps_std)).split('+/-')
            s = s.lstrip('0.').lstrip('0')
            text += '\nFPS: {}({})'.format(n, s)

        try:
            img = Image.open(io.BytesIO(self._socket.recv()))
        except zmq.ZMQError:
            return None
        else:
            draw = ImageDraw.Draw(img)
            draw.text((10, 10), text, (255, 106, 0), font=self._font)

            raw = io.BytesIO()
            img.save(raw, format='jpeg')
            return raw.getvalue()
