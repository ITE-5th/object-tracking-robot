import json
import netifaces as ni
import threading
import time

import RPi.GPIO as GPIO
from motor_controller import QuadMotorController
from pid import PID
from range_sensor import RangeSensor
from server import Server

t = 0.1
speed = 0

x = 0
y = 0
status = ""
width = 0
height = 0
x_min = 70
x_max = 200
maxArea = 800
minArea = 0
pid = PID()
range_sensor = RangeSensor()
motor_controller = QuadMotorController()

range_sensor_value = 0


def range_sensor_updater():
    global range_sensor_value
    print('range Sensor thread is running')

    while True:
        range_sensor_value = range_sensor.update()


def reverse(m_speed=0):
    if m_speed == 0:
        m_speed = None
    motor_controller.move_backward(back_speed=m_speed)
    # setLEDs(1, 0, 0, 1)
    # print('straight')


def forwards(m_speed=0):
    if m_speed == 0:
        m_speed = None
    if range_sensor_value > 30:
        motor_controller.move_forward(forward_speed=m_speed)
    # setLEDs(0, 1, 1, 0)
    # print('straight')


def turnright(m_speed=0):
    if m_speed == 0:
        m_speed = None
    motor_controller.move_right(right_speed=m_speed)
    # setLEDs(0, 0, 1, 1)
    # print('left')


def turnleft(m_speed=0):
    if m_speed == 0:
        m_speed = None
    motor_controller.move_left(left_speed=m_speed)
    # setLEDs(1, 1, 0, 0)
    # print('right')


def stopall():
    motor_controller.stopall()
    # setLEDs(1, 1, 1, 1)
    # print('stop')


def movement():
    global status, width, height, x_min, x_max, maxArea, minArea, x, y, pid
    print("started")

    while True:
        message, address = server.receive()
        message = message.decode("utf-8")
        print("Got >>", message, " form : ", address)
        json_message = json.loads(message)

        if "x_min" in message:
            x_min = json_message.get("x_min")
            x_max = json_message.get("x_max")
            maxArea = json_message.get("maxArea")
            minArea = json_message.get("minArea")
            pid.target = (minArea + maxArea) / 2
            print("Got Min and Max")

        if "status" in message:
            status = json_message.get("status")
            print("action: ", status)
            if status == "stop":
                # stop = True
                stopall()

        if "width" in message:
            x = json_message.get("x")
            y = json_message.get("y")
            width = json_message.get("width")
            height = json_message.get("height")
            print("x = {}, y = {}, width = {}, height = {}".format(x, y, width, height))

        FB = json_message.get("FB")

        LR = json_message.get("LR")

        # print FB + " " + LR + str(len(FB)) + str(len(LR))
        if FB == "F":
            forwards()
            pass
        elif FB == "B":
            reverse()
            pass

        elif LR == "L":
            turnleft()
            pass

        elif LR == "R":
            turnright()
            pass

        elif LR == "S" or FB == "S":
            # print 'stop'
            stopall()


def auto_movement():
    global status, width, height, x_min, x_max, maxArea, minArea, x, y, speed, pid
    while True:
        if status == 'run':
            area = width * height
            speed += pid.update(area)
            raw_speed = max(0, min(100, speed))
            print('******************************')
            print('speed is :{}'.format(speed))
            print('raw speed is : {}'.format(raw_speed))
            print('******************************')
            speed = max(0, min(100, speed))
            if x < x_min:
                turnleft(m_speed=raw_speed)
                time.sleep(0.1)
            elif x > x_max:
                turnright(m_speed=raw_speed)
                time.sleep(0.1)
            elif speed > 0:
                forwards(m_speed=raw_speed)
                time.sleep(0.2)
            elif speed < 0:
                raw_speed = max(0, min(100, -speed))
                reverse(m_speed=raw_speed)
                time.sleep(0.2)
            else:
                stopall()
            stopall()
            time.sleep(0.2)
        else:
            time.sleep(1)


if __name__ == '__main__':
    ip = ni.ifaddresses('wlan0')[ni.AF_INET][0]['addr']
    server = Server(host=ip)

    print('Server is online \nHost Name : {}:{}'.format(server.host_name, server.port))
    try:
        range_sensor_thread = threading.Thread(target=range_sensor_updater)
        movement_thread = threading.Thread(target=movement)
        auto_movement_thread = threading.Thread(target=auto_movement)

        range_sensor_thread.start()
        movement_thread.start()
        auto_movement_thread.start()

        range_sensor_thread.join()
        auto_movement_thread.join()
        movement_thread.join()
    finally:
        GPIO.cleanup()
        stopall()
