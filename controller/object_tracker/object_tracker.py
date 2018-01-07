from abc import ABCMeta, abstractmethod
from collections import deque

import cv2

from controller.object_tracker.position_predictor.velocity_position_predictor import VelocityPositionPredictor


class ObjectTracker(metaclass=ABCMeta):
    NO_OBJECT = "No_Object"

    def __init__(self, video_url=0, buffer_size=64, time_step=2, interpolater=VelocityPositionPredictor(4)):
        self.url = video_url
        self.buffer_size = buffer_size
        self.time_step = time_step
        self.positions = deque(maxlen=self.buffer_size)
        self.is_working = False
        self.interpolater = interpolater

    def track(self):
        self.is_working = True
        if self.url is None:
            camera = cv2.VideoCapture(0)
        else:
            camera = cv2.VideoCapture(self.url)
        try:
            while True:
                (grabbed, frame) = camera.read()
                if self.url is None and not grabbed:
                    return False
                if not self._track(frame):
                    return False
        finally:
            camera.release()
            cv2.destroyAllWindows()
            self.is_working = False

    @abstractmethod
    def _track(self, frame) -> bool:
        raise NotImplementedError()
