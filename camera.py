import io
import time
import picamera
from base_camera import BaseCamera


class Camera(BaseCamera):

    @staticmethod
    def frames():
        with picamera.PiCamera() as camera:
            camera.resolution = (640, 480)
            camera.framerate = 32
            camera.rotation = 180

            warm_up_time_in_seconds = 2.
            time.sleep(warm_up_time_in_seconds)

            stream = io.BytesIO()
            for _ in camera.capture_continuous(stream, 'jpeg',
                                               use_video_port=True):
                # return current frame
                stream.seek(0)
                yield stream.read()

                # reset stream for next frame
                stream.seek(0)
                stream.truncate()
