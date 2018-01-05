import time


class PID:

    def __init__(self, target=None, p=2.0, i=0.0, d=1.0, derivator=0, integrator=0, integrator_max=500,
                 integrator_min=-500):
        self.target = target
        self.kp = p
        self.ki = i
        self.kd = d
        self.p, self.d, self.i = 0, 0, 0
        self.derivator = derivator
        self.integrator = integrator
        self.integrator_max = integrator_max
        self.integrator_min = integrator_min
        self.error = 0.0

    def update(self, current_value):
        if self.target is None:
            return None
        self.error = self.target - current_value
        self.p = self.kp * self.error
        self.d = self.kd * (self.error - self.derivator)
        self.derivator = self.error
        self.integrator = self.integrator + self.error
        if self.integrator > self.integrator_max:
            self.integrator = self.integrator_max
        elif self.integrator < self.integrator_min:
            self.integrator = self.integrator_min
        self.i = self.integrator * self.ki
        return self.p + self.i + self.d


def percentage(part, whole):
    return 100 * float(part) / float(whole)


if __name__ == '__main__':
    target_area = 300
    current_area = 200
    # example
    pid = PID(target=target_area, p=1, i=0.4, d=0.01)
    while True:
        current_area += 1

        update = pid.update(current_area)
        new_index = max(-100, min(percentage(update, pid.target), 100))

        print('{}         {}'.format(update, new_index))
        # print(x)
        time.sleep(0.1)
