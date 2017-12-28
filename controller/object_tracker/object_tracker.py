from abc import ABCMeta, abstractmethod
from collections import deque

import cv2


class ObjectTracker(metaclass=ABCMeta):
    def __init__(self, video_url=0, buffer_size=64):
        self.url = video_url
        self.buffer_size = buffer_size
        # initial position x,y,r
        self.positions = deque(maxlen=self.buffer_size)
        self.is_working = False

    def track(self):
        self.is_working = True
        if self.url is None:
            camera = cv2.VideoCapture(0)
        else:
            camera = cv2.VideoCapture(self.url)
        try:
            while self._track(camera):
                pass
        finally:
            camera.release()
            cv2.destroyAllWindows()
            self.is_working = False


    @abstractmethod
    def _track(self, camera) -> bool:
        raise NotImplementedError()