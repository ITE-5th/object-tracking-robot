import sys
import threading
from queue import Queue

import cv2
from PyQt5 import QtCore, QtGui, uic, QtWidgets
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon

from controller.detectors.color_detector import ColorObjectDetector
from controller.detectors.yolo_detector import YoloObjectDetector
from controller.trackers.object_tracker import ObjectTracker
from desktop.image_widget import ImageWidget

FormClass = uic.loadUiType("ui.ui")[0]
running = True
image = None
bboxes = None
objects = None
labels = None
q = Queue()
capture = cv2.VideoCapture(0)


def setup_camera(width=1920, height=1080, fps=5):
    global capture
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    capture.set(cv2.CAP_PROP_FPS, fps)


def grab(q):
    global running
    global capture
    while running:
        capture.grab()
        _, img = capture.retrieve(0)
        q.put(img)


class Ui(QtWidgets.QMainWindow, FormClass):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.drawing_method = "matplotlib"
        self.with_prop = True
        self.window_width = self.videoWidget.frameSize().width()
        self.window_height = self.videoWidget.frameSize().height()
        self.videoWidget = ImageWidget(self.videoWidget, self)

        self.captureButton.clicked.connect(self.capture_image)
        self.yoloDetectorRB.clicked.connect(self.set_yolo_detector)
        self.colorDetectorRB.clicked.connect(self.set_color_detector)
        self.videoWidget.mousePressEvent = self.select_object

        self.set_image_on_button(self.captureButton, True)
        setup_camera()
        self.resume_camera()
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(1)

        self.yolo_detector = YoloObjectDetector()
        self.color_detector = ColorObjectDetector()

        self.detector = self.yolo_detector
        self.tracker = ObjectTracker()

    def set_yolo_detector(self):
        self.detector = self.yolo_detector

        global bboxes
        self.videoWidget.setBBoxes(bboxes)

    def set_color_detector(self):
        self.detector = self.color_detector
        self.videoWidget.setBBoxes(None)

    def item_selected(self, item):
        self.detector.set_classes([item])

    def select_object(self, event):
        global running
        if running or self.detector is not self.yolo_detector:
            return

        global bboxes
        self.videoWidget.setBBoxes(bboxes)

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
        global q
        capture_thread = threading.Thread(target=grab, args=[q])
        capture_thread.start()

    def capture_image(self):
        global running
        global q
        self.set_image_on_button(self.captureButton, not running)
        if running:
            running = False
        else:
            running = True
            q.queue.clear()
            self.resume_camera()

    def set_image(self, image_path):
        pixmap = QtGui.QPixmap(image_path)
        scaled_pixmap = pixmap.scaled(self.imageLabel.size(), Qt.KeepAspectRatio)
        self.imageLabel.setPixmap(scaled_pixmap)

    def update_frame(self):
        global running
        if not q.empty() and running:
            self.videoWidget.setBBoxes(None)
            img = q.get()

            if self.detector == self.yolo_detector:
                global image, bboxes
                img, bboxes = self.yolo_detector.detect_all(img, self.window_width, self.window_height)
            else:
                img = cv2.resize(img, (self.window_width, self.window_height), interpolation=cv2.INTER_CUBIC)

            height, width, bpc = img.shape
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            bpl = bpc * width

            image = QtGui.QImage(img.data, width, height, bpl, QtGui.QImage.Format_RGB888)
            self.videoWidget.setImage(image, img)

    def closeEvent(self, event):
        global running
        running = False


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    # with open("qdarkstyle/style.qss") as f:
    #     app.setStyleSheet(f.read())
    ui = Ui()
    ui.show()
    app.exec_()
