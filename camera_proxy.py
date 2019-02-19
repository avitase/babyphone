import time

import zmq


class CameraProxy(object):
    def __init__(self, socket):
        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.REQ)
        self._socket.connect(socket)
        self._last_update = time.time()

    def get_frame(self):
        self._socket.send_string('')
        self._last_update = time.time()
        return self._socket.recv()
