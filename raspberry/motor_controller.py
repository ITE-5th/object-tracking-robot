"""
   Servo Example - Example of usage ASMpi class
"""
from AMSpi import AMSpi
import time


class QuadMotorController:
    _AMSPI = AMSpi(use_board=False)

    def __init__(self, _74HC595_pins=None, L293D_pins=None):

        if _74HC595_pins is None:
            _74HC595_pins = [21, 20, 16]
        if L293D_pins is None:
            L293D_pins = [5, 6, 13, 19]

        self._AMSPI.set_74HC595_pins(_74HC595_pins[0], _74HC595_pins[1], _74HC595_pins[2])
        self._AMSPI.set_L293D_pins(L293D_pins[0], L293D_pins[1], L293D_pins[2], L293D_pins[3])

    def move_forward(self, forward_speed=None):
        print("GO: clockwise")
        self._AMSPI.run_dc_motors(
            [self._AMSPI.DC_Motor_1, self._AMSPI.DC_Motor_2, self._AMSPI.DC_Motor_3, self._AMSPI.DC_Motor_4],
            speed=forward_speed)
        return True

    def move_backward(self, back_speed=None):
        print("GO: counterclockwise")
        self._AMSPI.run_dc_motors(
            [self._AMSPI.DC_Motor_1, self._AMSPI.DC_Motor_2, self._AMSPI.DC_Motor_3, self._AMSPI.DC_Motor_4],
            clockwise=False,
            speed=back_speed)

    def move_right(self, right_speed=None):
        print("Turn right")
        self._AMSPI.run_dc_motors([self._AMSPI.DC_Motor_1, self._AMSPI.DC_Motor_2], clockwise=False, speed=right_speed)
        self._AMSPI.run_dc_motors([self._AMSPI.DC_Motor_3, self._AMSPI.DC_Motor_4], speed=right_speed)

    def move_left(self, left_speed=None):
        print("Turn left")
        self._AMSPI.run_dc_motors([self._AMSPI.DC_Motor_1, self._AMSPI.DC_Motor_2], speed=left_speed)
        self._AMSPI.run_dc_motors([self._AMSPI.DC_Motor_3, self._AMSPI.DC_Motor_4], clockwise=False, speed=left_speed)

    def stopall(self):
        print("Stop")
        self._AMSPI.stop_dc_motors(
            [self._AMSPI.DC_Motor_1, self._AMSPI.DC_Motor_2, self._AMSPI.DC_Motor_3, self._AMSPI.DC_Motor_4])


# Test Main

if __name__ == '__main__':
    x = QuadMotorController()
    x.move_forward()
    x.stopall()
    x.move_backward()
    x.stopall()
    x.move_right()
    x.stopall()
    x.move_left()
    x.stopall()

    while True:  # making a loop
        print('waiting')
        try:  # used try so that if user pressed other than the given key error will not be shown
            k = input()
            if k == 'w':  # if key 'q' is pressed
                x.move_forward()
            elif k == 's':  # if key 'q' is pressed
                x.move_backward()
            elif k == 'd':  # if key 'q' is pressed
                x.move_right()
            elif k == 'a':  # if key 'q' is pressed
                x.move_left()
            elif k == 'q':  # if key 'q' is pressed
                print('You Pressed Q Key!')
                break  # finishing the loop
            else:
                pass
        except:
            break  # if user pressed other than the given key the loop will break
