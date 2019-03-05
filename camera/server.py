import configparser
import functools
import logging
import os
import signal
from importlib import import_module

if os.environ.get('CAMERA'):
    Camera = import_module('camera_' + os.environ['CAMERA']).Camera
else:
    from camera_test import Camera


def exit_gracefully(signum, frame, camera):
    camera.stop()


def init_logger(log_level):
    logger = logging.getLogger('camera')
    logger.setLevel(log_level)

    handler = logging.StreamHandler()
    handler.setLevel(log_level)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')

    config_get = lambda sec, key, fllbck: config[sec].get(key, fllbck) if sec in config else fllbck

    log_level = config_get('LOGGING', 'LOG_LEVEL', 'INFO')
    logger = init_logger(log_level)
    logger.info('Setting log level to {}'.format(log_level))

    socket = config_get('CAMERA', 'SOCKET', 'ipc:///tmp/camera.socket')
    max_fps = int(config_get('CAMERA', 'MAX_FPS', '40'))
    logger.info('Connecting camera to \'{}\' and limit FPS by {}'.format(socket, max_fps))
    camera = Camera(socket=socket, max_fps=max_fps)

    do_exit = functools.partial(exit_gracefully, camera=camera)
    signal.signal(signal.SIGINT, do_exit)
    signal.signal(signal.SIGTERM, do_exit)

    logger.info('Starting camera')
    camera.run()
