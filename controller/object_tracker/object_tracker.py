import numpy as np
from sklearn.svm import SVR
from abc import ABCMeta, abstractmethod
from collections import deque

import cv2


class ObjectTracker(metaclass=ABCMeta):
    def __init__(self, video_url=0, buffer_size=64, time_step=2):
        self.url = video_url
        self.buffer_size = buffer_size
        self.time_step = time_step
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
                next_position = self.predict_next_position()
        finally:
            camera.release()
            cv2.destroyAllWindows()
            self.is_working = False

    def predict_next_position(self):
        if len(self.positions) <= 30:
            return
        svr = SVR()
        positions = list(reversed(self.positions))
        x = np.arange(1, len(positions) + 1).reshape(-1, 1)
        y = [[x, y, width, height] for x, y, width, height, _ in positions]
        y = np.array(y)
        svr.fit(x, y)
        predicted = svr.predict(np.array([len(self.positions) + self.time_step + 1]))
        return predicted[0]

    @abstractmethod
    def _track(self, camera) -> bool:
        raise NotImplementedError()
