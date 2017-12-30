import numpy as np

from controller.object_tracker.position_predictor.position_predictor import PositionPredictor


class RegressorPositionPredictor(PositionPredictor):
    def __init__(self, regressor, time_step=2):
        super().__init__(time_step)
        self.regressor = regressor
        self.time_step = time_step

    def _predict(self, positions):
        x = np.arange(1, len(positions) + 1).reshape(-1, 1)
        y = [[x, y, width, height] for x, y, width, height, _ in positions]
        y = np.array(y)
        self.regressor.fit(x, y)
        predicted = self.regressor.predict(np.array([[len(positions) + self.time_step + 1]]))
        return predicted[0]
