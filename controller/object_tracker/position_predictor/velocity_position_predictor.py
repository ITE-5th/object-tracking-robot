from controller.object_tracker.position_predictor.position_predictor import PositionPredictor


class VelocityPositionPredictor(PositionPredictor):
    def __init__(self, interpolation_length=4, time_step=2):
        super().__init__(time_step)
        self.intercepts = []
        for i in range(interpolation_length - 1):
            self.intercepts.append(1 / (2 ** i))

    def _predict(self, positions):
        if len(positions) < len(self.intercepts):
            return None
        positions = positions[:len(self.intercepts) + 1]
        for i in range(self.time_step):
            positions.insert(0, self._predict_next(positions))
            positions = positions[:-1]

    def _predict_next(self, positions):
        result = (0, 0, 0, 0)
        for i in range(len(self.intercepts)):
            inter = self.intercepts[i]
            second, first = positions[i], positions[i + 1]
            diff = (second[0] - first[0], second[1] - first[1], second[2] - first[2], second[3] - first[3])
            result = (result[0] + inter * diff[0], result[1] + inter * diff[1], result[2] + inter * diff[2],
                      result[3] + inter * diff[3])
        return positions[0][0] + result[0], positions[0][1] + result[1], positions[0][2] + result[2], positions[0][3] + \
               result[3]
