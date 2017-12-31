import json
import sys
import threading
import time
from queue import Queue

import cv2
# from PySide import QtGui
import qdarkstyle
from PyQt5 import QtCore, QtGui, uic, QtWidgets
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QLabel, QColorDialog

from controller.client import Client
from controller.detectors.color_detector import ColorObjectDetector
from controller.detectors.detector import ObjectDetector
from controller.detectors.yolo_detector import YoloObjectDetector
from controller.trackers.object_tracker import ObjectTracker
from desktop.image_widget import ImageWidget

FormClass = uic.loadUiType("ui.ui")[0]


class Ui(QtWidgets.QMainWindow, FormClass):
    RUN = 'run'
    STOP = 'stop'
    MANUAL = 'manual'
    NO_OBJECT = ObjectDetector.NO_OBJECT

    def __init__(self, host='raspberrypi', port=1234, url=None):
        QtWidgets.QMainWindow.__init__(self)
        self.setupUi(self)

        self.running = True
        self.capture = None
        self.selected_classes = None
        self.status = self.STOP
        self.yolo_detector = YoloObjectDetector()
        self.color_detector = ColorObjectDetector()
        self.bboxes = None
        self.queue = Queue()

        self.tracker = ObjectTracker()
        self.tracker.set_detector(self.yolo_detector)
        self.client = Client(host=host, port=port)
        self.timer = QtCore.QTimer(self)
        self.colorPickerButton.clicked.connect(self.color_picker)

        self.setup_camera(url)

        self.trackButton.clicked.connect(self.start_tracking)
        self.forceStopButton.clicked.connect(self.stop_tracking)
        self.setButton.clicked.connect(self.robot_initializer)

        self.window_width = self.videoWidget.frameSize().width()
        self.window_height = self.videoWidget.frameSize().height()
        self.videoWidget = ImageWidget(self.videoWidget, self)

        self.captureButton.clicked.connect(self.capture_image)
        self.yoloDetectorRB.clicked.connect(self.set_yolo_detector)
        self.colorDetectorRB.clicked.connect(self.set_color_detector)
        self.videoWidget.mousePressEvent = self.select_object

        self.set_image_on_button(self.captureButton, True)

        self.resume_camera()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(1)

        self.statusBar.addWidget(QLabel("Status: "))
        self.statusLabel = QLabel("Initialization")
        self.statusBar.addWidget(self.statusLabel)

    def setup_camera(self, url=None, width=1920, height=1080, fps=5):
        if url is None:
            self.capture = cv2.VideoCapture(0)
        else:
            self.capture = cv2.VideoCapture(url)

        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.capture.set(cv2.CAP_PROP_FPS, fps)

    def grab(self):
        while self.running:
            self.capture.grab()
            _, img = self.capture.retrieve(0)
            self.queue.put(img)

    def keyPressEvent(self, event1):
        self.set_status(self.MANUAL)

        verbose = {"FB": "", "LR": ""}
        if event1.key() == QtCore.Qt.Key_W:
            # print "Up pressed"
            verbose["FB"] = "F"
        if event1.key() == QtCore.Qt.Key_S:
            # print "D pressed"
            verbose["FB"] = "B"

        if event1.key() == QtCore.Qt.Key_A:
            # print "L pressed"
            verbose["LR"] = "L"
        if event1.key() == QtCore.Qt.Key_D:
            # print "R pressed"
            verbose["LR"] = "R"

        json_data = json.dumps(verbose)
        if verbose["LR"] != "" or verbose["FB"] != "":
            print(verbose)
            self.client.send(json_data)

    def keyReleaseEvent(self, event):
        verbose = {"FB": "", "LR": ""}
        if event.key() == QtCore.Qt.Key_W:
            # print "Up rel"
            verbose["FB"] = "S"
        if event.key() == QtCore.Qt.Key_S:
            # print "D rel"
            verbose["FB"] = "S"

        if event.key() == QtCore.Qt.Key_A:
            # print "L pressed"
            verbose["LR"] = "S"
        if event.key() == QtCore.Qt.Key_D:
            # print "R pressed"
            verbose["LR"] = "S"

        json_data = json.dumps(verbose)
        if verbose["LR"] != "" or verbose["FB"] != "":
            print(verbose)
            self.client.send(json_data)
            self.client.send(json_data)

    def color_picker(self):
        a = QColorDialog
        a.setCurrentColor(self.color_detector.get_default_color())
        color = QColorDialog.getColor()
        print(color.getRgb())
        self.colorPickerButton.setStyleSheet("background-color: %s" % (color.name()))
        # self.colorPickerButton.setStyle
        # self.color_detector.set_color(color)

    def start_tracking(self):
        self.set_status(self.RUN)

        # if self.tracker.is_tracking():
        self.tracker.set_tracking(True)
        self.tracker.detector.set_classes(self.selected_classes)

        print('start tracking')
        verbose = {
            "status": self.RUN
        }
        json_data = json.dumps(verbose)
        self.client.send(json_data)

        data_sender_thread = threading.Thread(target=self.data_sender)
        data_sender_thread.start()

    def stop_tracking(self):

        self.tracker.detector.set_classes(None)
        self.tracker.set_tracking(False)
        self.set_status(self.STOP)
        verbose = {
            "status": self.STOP
        }
        json_data = json.dumps(verbose)
        self.client.send(json_data)

    def robot_initializer(self):

        try:
            x_min = round(float(self.minXEdit.text()), 2)
        except:
            x_min = 200

        try:
            x_max = round(float(self.maxXEdit.text()), 2)
        except:
            x_max = 300
        try:
            minArea = round(float(self.minAreaEdit.text()), 2)
        except:
            minArea = 20
        try:
            maxArea = round(float(self.maxAreaEdit.text()), 2)
        except:
            maxArea = 100

        verbose = {
            "x_min": x_min,
            "x_max": x_max,
            "maxArea": maxArea,
            "minArea": minArea,
        }
        json_data = json.dumps(verbose)
        print(json_data)
        self.client.send(json_data)

    def data_sender(self):
        verbose = {}

        prev_position = [0, 0, 0, 0]
        while self.tracker.is_tracking() and self.status != self.STOP:
            if self.tracker.has_positions():
                currentPosition = self.tracker.positions[0]
                if currentPosition[0] is not None and self.status != self.NO_OBJECT and max_diff(currentPosition,
                                                                                                 prev_position) > 10:
                    print(currentPosition)
                    verbose["x"] = currentPosition[0]
                    verbose["y"] = currentPosition[1]
                    verbose["width"] = currentPosition[2]
                    verbose["height"] = currentPosition[3]
                    json_data = json.dumps(verbose)
                    self.client.send(json_data)
                    prev_position = currentPosition
                if currentPosition[4] == self.NO_OBJECT:
                    self.set_status(self.NO_OBJECT)
                elif self.status == self.NO_OBJECT:
                    self.set_status(self.RUN)
            time.sleep(0.2)
        self.set_status(self.STOP)

    def set_status(self, status):
        self.status = status
        self.statusLabel.setText(self.status)

    def set_yolo_detector(self):
        self.tracker.set_detector(self.yolo_detector)
        self.videoWidget.setBBoxes(self.bboxes)

    def set_color_detector(self):
        self.tracker.set_detector(self.color_detector)
        self.videoWidget.setBBoxes(None)

    def item_selected(self, item):
        self.selected_classes = [item]

    def select_object(self, event):
        if self.running or self.tracker.detector is not self.yolo_detector:
            return

        self.videoWidget.setBBoxes(self.bboxes)

    @staticmethod
    def set_image_on_button(button, stop: bool):
        if stop:
            pixmap = QPixmap("icons/cam_record.png")
        else:
            pixmap = QPixmap("icons/cam_stop.png")

        buttonIcon = QIcon(pixmap)
        button.setIcon(buttonIcon)
        size = QSize(50, 50)
        button.setIconSize(size)

    def resume_camera(self):
        # 1920, 1080, 30
        self.videoWidget.setBBoxes(None)
        capture_thread = threading.Thread(target=self.grab)
        capture_thread.start()

    def capture_image(self):
        self.set_image_on_button(self.captureButton, not self.running)
        if self.running:
            self.running = False
        else:
            self.running = True
            self.queue.queue.clear()
            self.resume_camera()

    def set_image(self, image_path):
        pixmap = QtGui.QPixmap(image_path)
        scaled_pixmap = pixmap.scaled(self.imageLabel.size(), Qt.KeepAspectRatio)
        self.imageLabel.setPixmap(scaled_pixmap)

    def update_frame(self):
        if not self.queue.empty() and self.running:
            self.videoWidget.setBBoxes(None)
            img = self.queue.get()

            img = cv2.resize(img, (self.window_width, self.window_height), interpolation=cv2.INTER_CUBIC)

            # if self.tracker.is_tracking():
            #     new_img = self.tracker.track(img)
            # else:
            #     new_img, self.bboxes = self.tracker.detector.detect_all(img)

            new_img, self.bboxes = self.tracker.track(img)

            height, width, bpc = new_img.shape
            new_img = cv2.cvtColor(new_img, cv2.COLOR_BGR2RGB)
            bpl = bpc * width

            image = QtGui.QImage(new_img.data, width, height, bpl, QtGui.QImage.Format_RGB888)
            self.videoWidget.setImage(image, img)

    def closeEvent(self, event):
        self.running = False

        self.status = self.STOP
        verbose = {
            "status": self.STOP
        }
        json_data = json.dumps(verbose)
        self.client.send(json_data)
        QtCore.QCoreApplication.instance().quit()


# Helper function

def max_diff(current_position, prev_position):
    max_var = max(abs(current_position[0] - prev_position[0]), abs(current_position[1] - prev_position[1]),
                  abs(current_position[2] - prev_position[2]), abs(current_position[3] - prev_position[3]))
    return max_var


def main(ip, port, url=None):
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    ui = Ui(host=ip, port=port, url=url)
    ui.showMaximized()

    app.exec_()


if __name__ == '__main__':
    videoURL = "http://raspberrypi:8080/stream/video.mjpeg"
    IP = "raspberrypi"
    # IP = "localhost"
    PORT = 1234

    main(ip=IP, port=PORT, url=videoURL)
