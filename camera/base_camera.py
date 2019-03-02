import time

import zmq


class BaseCamera(object):
    def __init__(self, socket):
        self.MAX_FPS = 40

        context = zmq.Context()
        self._socket = context.socket(zmq.REP)
        self._socket.bind(socket)

        self.is_running = False

    def stop(self):
        self.is_running = False

    def run(self):
        now = time.time
        t = now()

        self.is_running = True
        while self.is_running:
            frame = self.next_frame()

            requests_left = True
            while requests_left:
                try:
                    self._socket.recv(flags=zmq.NOBLOCK)
                except zmq.ZMQError:
                    requests_left = False
                else:
                    self._socket.send(frame)

            dt = 1. / float(self.MAX_FPS) - (now() - t)
            if dt > 0.:
                time.sleep(dt)
            t = now()

    def next_frame(self):
        raise RuntimeError('Must be implemented by subclasses.')
