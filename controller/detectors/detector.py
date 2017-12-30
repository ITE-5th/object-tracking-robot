from abc import ABCMeta, abstractmethod


class ObjectDetector(metaclass=ABCMeta):
    @abstractmethod
    def _detect(self, image, window_width, window_height):
        raise NotImplementedError()

    @abstractmethod
    def _detect_all(self, image, window_width, window_height):
        raise NotImplementedError()

    def detect(self, image, window_width, window_height):
        return self._detect(image, window_width, window_height)

    def detect_all(self, image, window_width, window_height):
        return self._detect_all(image, window_width, window_height)
