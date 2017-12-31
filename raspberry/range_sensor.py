#!/usr/bin/env python

# HC_SR04.py
# 2015-08-06
# Public Domain
import time

import pigpio


class sensor:

    def __init__(self, pi, trigger, echo):

        self._pi = pi
        self._trig = trigger
        self._echo = echo

        self._tick = None
        self._distance = 0.0
        self._new = False

        pi.set_mode(self._trig, pigpio.OUTPUT)
        pi.set_mode(self._echo, pigpio.INPUT)

        self._cb = pi.callback(self._echo, pigpio.EITHER_EDGE, self._cbf)

    def _cbf(self, gpio, level, tick):

        if level == 1:
            self._tick = tick
        else:
            if self._tick is not None:
                ping = pigpio.tickDiff(self._tick, tick)
                self._distance = ping * 17015.0 / 1000000.0
                self._new = True

    def trigger(self):

        self._tick = None
        self._pi.gpio_trigger(self._trig, 10)

    def get_centimetres(self):

        new = self._new
        self._new = False
        return self._distance, new

    def cancel(self):

        self._cb.cancel()


if __name__ == "__main__":

    pi = pigpio.pi()

    sonar = sensor(pi, trigger=23, echo=24)

    end = time.time() + 1000.0

    r = 1
    while time.time() < end:
        sonar.trigger()
        time.sleep(0.1)
        cms, new = sonar.get_centimetres()
        print("{} {:.1f} {}".format(r, cms, new))
        r += 1

    sonar.cancel()

    pi.stop()

# import time
#
# import RPi.GPIO as GPIO
#
#
# class RangeSensor:
#
#     def __init__(self, trig=23, echo=24):
#         GPIO.setmode(GPIO.BCM)
#         self.TRIG = trig
#         self.ECHO = echo
#         GPIO.setup(self.TRIG, GPIO.OUT)
#         GPIO.setup(self.ECHO, GPIO.IN)
#         GPIO.output(self.TRIG, False)
#         print("Waiting For Sensor To Settle")
#         time.sleep(2)
#
#     def update(self):
#         time.sleep(0.1)
#         GPIO.output(self.TRIG, True)
#         time.sleep(0.00001)
#         GPIO.output(self.TRIG, False)
#         pulse_start = 0
#         pulse_end = 10
#         while GPIO.input(self.ECHO) == 0:
#             pulse_start = time.time()
#
#         while GPIO.input(self.ECHO) == 1:
#             pulse_end = time.time()
#         pulse_duration = pulse_end - pulse_start
#         distance = pulse_duration * 17150
#
#         return round(distance, 2)
