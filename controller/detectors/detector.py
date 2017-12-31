from abc import ABCMeta, abstractmethod


class ObjectDetector(metaclass=ABCMeta):
    NO_OBJECT = "No_Object"

    @abstractmethod
    def _detect(self, image):
        raise NotImplementedError()

    @abstractmethod
    def _detect_all(self, image):
        raise NotImplementedError()

    def detect(self, image):
        return self._detect(image)

    def detect_all(self, image):
        return self._detect_all(image)

    @abstractmethod
    def set_classes(self, classes):
        raise NotImplementedError()