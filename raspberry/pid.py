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


if __name__ == '__main__':
    # example
    pid = PID(2)
    y = 0
    x = 0
    while True:
        x += pid.update(y)
        y += 1
        print(x)
