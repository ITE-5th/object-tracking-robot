import json
import threading
import time

import RPi.GPIO as GPIO
import netifaces as ni
import pigpio
from motor_controller import QuadMotorController
from pid import PID
from range_sensor import sensor
from server import Server

# from raspberry.motor_controller import QuadMotorController
# from raspberry.pid import PID
# from raspberry.range_sensor import sensor
# from raspberry.server import Server


run = 'Running'
STOP = 'Stopped'
MANUAL = 'Manual'

fb_speed = 0
lr_speed = 0

x = 500
y = 0
area = 7000
x_min = 200
x_max = 800

fb_pid = PID(target=10000, p=0.5, i=0, d=0.5)
lr_pid = PID(target=500, p=1, i=0, d=0.5)

motor_controller = QuadMotorController()

range_sensor_value = 100

no_object = "no_object"
motor_status = 'stop'
status = STOP
# Used For optimizing no object status

is_keep_track = False
is_balanced = True
no_obj_flag = False


def range_sensor_updater():
    global range_sensor_value
    print('range Sensor thread is running')
    pi = pigpio.pi()
    sonar = sensor(pi, trigger=23, echo=24)
    while True:
        try:
            sonar.trigger()
            time.sleep(0.1)
            cms, new = sonar.get_centimetres()
            range_sensor_value = 100
            # if new:
            #     range_sensor_value = cms
            #     # print('range : {}'.format(range_sensor_value))
        except Exception as e:
            print('range Sensor thread is stopped')
            print(e)
            sonar.cancel()
            pi.stop()


def reverse(m_speed=None):
    global motor_controller, motor_status
    try:
        # if motor_status != 'backward':
        #     time.sleep(0.1)
        motor_status = 'backward'
        motor_controller.move_backward(back_speed=m_speed)
    # setLEDs(1, 0, 0, 1)
    # print('straight')
    except:
        motor_controller = QuadMotorController()


def forwards(m_speed=None):
    global motor_controller, motor_status
    try:
        motor_status = 'forward'
        if range_sensor_value > 30:
            motor_controller.move_forward(forward_speed=m_speed)
        else:
            print('RANGE SENSOR : {} cm'.format(range_sensor_value))
    except:
        motor_controller = QuadMotorController()


def turnright(m_speed=None):
    global motor_controller, motor_status
    try:
        motor_status = 'right'
        motor_controller.move_right(right_speed=m_speed)
    except:
        motor_controller = QuadMotorController()


def turnleft(m_speed=None):
    global motor_controller, motor_status
    try:
        motor_status = 'left'
        motor_controller.move_left(left_speed=m_speed)
    except:
        motor_controller = QuadMotorController()


def stopall(force=False):
    global motor_controller, motor_status
    try:
        if force:
            motor_controller.stopall()
        else:
            motor_controller.move_left(left_speed=0)
        motor_status = 'stop'
    except:
        motor_controller = QuadMotorController()


def movement():
    global status, width, height, x_min, x_max, maxArea, minArea, x, y, fb_pid, lr_pid, area, no_obj_flag, is_keep_track
    print("started")

    while True:
        message, address = server.receive()
        message = message.decode("utf-8")
        print("Got >>", message, " form : ", address)
        json_message = json.loads(message)

        if "kp_f" in message:
            fb_pid.kp = json_message.get("kp_f")
            fb_pid.ki = json_message.get("ki_f")
            fb_pid.kd = json_message.get("kd_f")

            lr_pid.kp = json_message.get("kp_s")
            lr_pid.ki = json_message.get("ki_s")
            lr_pid.kd = json_message.get("kd_s")

        if "x_min" in message:
            x_min = json_message.get("x_min")
            x_max = json_message.get("x_max")
            maxArea = json_message.get("maxArea")
            minArea = json_message.get("minArea")
            is_keep_track = json_message.get("keepTrack")
            fb_pid.target = (minArea + maxArea) / 2
            lr_pid.target = (x_min + x_max) / 2

            print("Got Min and Max")

        if "status" in message:
            status = json_message.get("status")
            print("action: ", status)
            if status == STOP:
                # stop = True
                stopall()

        if "width" in message:
            x = json_message.get("x")
            y = json_message.get("y")
            width = json_message.get("width")
            height = json_message.get("height")
            area = width * height
            print("x = {}, y = {}, width = {}, height = {}".format(x, y, width, height))
            if x == 0 and y == 0 and width == 0 and height == 0:
                if is_keep_track:
                    no_obj_flag = True
                else:
                    status = no_object
            elif status == no_object:
                status = run
                no_obj_flag = False

        FB = json_message.get("FB")

        LR = json_message.get("LR")

        manual_speed = 50
        # print FB + " " + LR + str(len(FB)) + str(len(LR))
        if FB == "F":
            forwards(m_speed=manual_speed)
            pass
        elif FB == "B":
            reverse(m_speed=manual_speed)
            pass

        elif LR == "L":
            turnleft(m_speed=manual_speed)
            pass

        elif LR == "R":
            turnright(m_speed=manual_speed)
            pass

        elif LR == "S" or FB == "S":
            # print 'stop'
            stopall()


# Helper Function
def percentage(part, whole):
    return 100 * float(part) / float(whole)


def map(value, istart, istop, ostart, ostop):
    return ostart + (ostop - ostart) * ((value - istart) / (istop - istart))


def auto_movement():
    global status, x_min, x_max, maxArea, minArea, x, y, fb_speed, lr_speed, fb_pid, area, is_balanced, no_obj_flag
    last_turn = 'L'
    no_object_loops = 0
    while True:
        if status == run:

            no_object_loops = 0

            # Calculate PID updates

            fb_update = fb_pid.update(area)
            fb_speed = percentage(fb_update, fb_pid.target)
            #
            is_forward = fb_speed > 20
            is_backward = fb_speed < -20

            fb_speed = max(0, min(100, abs(int(fb_speed))))
            fb_speed = int(map(fb_speed, 0, 100, 0, 100))

            lr_update = lr_pid.update(x)
            lr_speed = percentage(lr_update, lr_pid.target)
            #
            is_left = lr_speed > 30
            is_right = lr_speed < -30
            #
            lr_speed = max(0, min(100, abs(int(lr_speed))))
            lr_speed = int(map(lr_speed, 0, 100, 0, 75))

            print_status(area, fb_speed, is_left, is_right, lr_speed)

            if is_left:
                turnleft(m_speed=lr_speed)
                x += 100 * (lr_speed / 100)
                last_turn = 'L'
            elif is_right:
                turnright(m_speed=lr_speed)
                x -= 100 * (lr_speed / 100)
                last_turn = 'R'
            elif is_forward:
                forwards(m_speed=fb_speed)
                area += 400 * (fb_speed / 100)
            elif is_backward:
                reverse(m_speed=fb_speed)
                area -= 400 * (fb_speed / 100)

            if no_obj_flag and not is_left and not is_right and not is_forward and not is_backward:
                status = no_object
            time.sleep(0.05)
            stopall()
        elif status == no_object:
            print('********** No Object **********')
            if no_object_loops < 10:
                no_object_loops += 1
                if last_turn == 'R':
                    turnright(m_speed=50)
                else:
                    turnleft(m_speed=50)
                time.sleep(0.1)
                stopall()
                time.sleep(0.5)
        else:
            time.sleep(1)


def print_status(area, fb_speed, is_left, is_right, lr_speed):
    print('******************************')
    print('lr speed is :{} {} {}'.format(lr_speed, is_right, is_left))
    print('x is :{}'.format(area))
    print('******************************')
    print('******************************')
    print('fb speed is :{} {} {}'.format(fb_speed, is_right, is_left))
    print('area is :{}'.format(area))
    print('******************************')


if __name__ == '__main__':
    ip = ni.ifaddresses('wlan0')[ni.AF_INET][0]['addr']
    server = Server(host=ip)

    print('Server is online \nHost Name : {}:{}'.format(server.host_name, server.port))
    try:
        range_sensor_thread = threading.Thread(target=range_sensor_updater)
        movement_thread = threading.Thread(target=movement)
        auto_movement_thread = threading.Thread(target=auto_movement)
        # range_sensor_thread.start()
        movement_thread.start()
        auto_movement_thread.start()

        #  Join Thread to Stop together
        # range_sensor_thread.join()
        movement_thread.join()
        auto_movement_thread.join()

    finally:
        # Force STOP MOTORS
        stopall(force=True)
        GPIO.cleanup()
