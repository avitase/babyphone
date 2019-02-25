import functools
import os
import signal
from importlib import import_module

import settings_camera

if os.environ.get('CAMERA'):
    Camera = import_module('camera_' + os.environ['CAMERA']).Camera
else:
    from camera_test import Camera


def exit_gracefully(signum, frame, camera):
    camera.stop()


if __name__ == '__main__':
    camera = Camera(socket=settings_camera.CAMERA_SOCKET)

    do_exit = functools.partial(exit_gracefully, camera=camera)
    signal.signal(signal.SIGINT, do_exit)
    signal.signal(signal.SIGTERM, do_exit)

    camera.run()
