import sys

import qdarkstyle
from PyQt5 import QtWidgets

from desktop.ui import Ui


def main(ip, port, url=None):
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    ui = Ui(host=ip, port=port, url=url)
    ui.showMaximized()

    app.exec_()


if __name__ == '__main__':
    videoURL = "http://raspberrypi:8080/stream/video.mjpeg"
    IP = "raspberrypi"
    PORT = 1234

    main(ip=IP, port=PORT, url=videoURL)
