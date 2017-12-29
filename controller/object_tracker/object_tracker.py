from abc import ABCMeta, abstractmethod
from collections import deque

import cv2


class ObjectTracker(metaclass=ABCMeta):
    def __init__(self, video_url=0, buffer_size=64, time_step=2, interpolation_length=4):
        self.url = video_url
        self.buffer_size = buffer_size
        self.time_step = time_step
        self.positions = deque(maxlen=self.buffer_size)
        self.is_working = False
        self.intercepts = []
        for i in range(interpolation_length - 1):
            self.intercepts.append(1 / (2 ** i))

    def track(self):
        self.is_working = True
        if self.url is None:
            camera = cv2.VideoCapture(0)
        else:
            camera = cv2.VideoCapture(self.url)
        try:
            while self._track(camera):
                next_position = self.predict_next_position()
        finally:
            camera.release()
            cv2.destroyAllWindows()
            self.is_working = False

    def predict_next_position(self):
        if len(self.positions) < len(self.intercepts):
            return
        positions = list(reversed(self.positions))[:len(self.intercepts) + 1]
        result = (0, 0, 0)
        for i in range(len(self.intercepts)):
            inter = self.intercepts[i]
            second, first = positions[i], positions[i + 1]
            diff = (second[0] - first[0], second[1] - first[1], second[2] - first[2], first[3] * second[3])
            result = (result[0] + inter * diff[0], result[1] + inter * diff[1], result[2] + inter * diff[2],
                      result[3] + inter * diff[3])
        return positions[0][0] + result[0], positions[0][1] + result[1], positions[0][2] + result[2], positions[0][3] + result[3]

    @abstractmethod
    def _track(self, camera) -> bool:
        raise NotImplementedError()
