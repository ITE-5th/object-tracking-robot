from abc import ABCMeta, abstractmethod


class PositionPredictor(metaclass=ABCMeta):
    def __init__(self, time_step=2):
        self.time_step = time_step

    def predict(self, positions):
        positions = list(positions)
        return self._predict(positions)

    @abstractmethod
    def _predict(self, positions):
        raise NotImplementedError()
