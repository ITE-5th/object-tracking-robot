import time

import RPi.GPIO as GPIO


class RangeSensor:

    def __init__(self, trig=23, echo=24):
        GPIO.setmode(GPIO.BCM)
        self.TRIG = trig
        self.ECHO = echo
        GPIO.setup(self.TRIG, GPIO.OUT)
        GPIO.setup(self.ECHO, GPIO.IN)
        GPIO.output(self.TRIG, False)
        print("Waiting For Sensor To Settle")
        time.sleep(2)

    def update(self):
        time.sleep(0.1)
        GPIO.output(self.TRIG, True)
        time.sleep(0.00001)
        GPIO.output(self.TRIG, False)
        pulse_start = 0
        pulse_end = 10
        while GPIO.input(self.ECHO) == 0:
            pulse_start = time.time()

        while GPIO.input(self.ECHO) == 1:
            pulse_end = time.time()
        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150

        return round(distance, 2)
