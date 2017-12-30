import functools

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QMenu

from desktop.bboxes import bboxes_in_position


class ImageWidget(QtWidgets.QWidget):

    def __init__(self, parent=None, container=None):
        super().__init__(parent)
        self.raw_image = None
        self.image = None
        self.bboxes = None
        self.container = container

    def setImage(self, image, raw_image):
        self.image = image
        self.raw_image = raw_image
        sz = image.size()
        self.setMinimumSize(sz)
        self.update()

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        if self.image:
            qp.drawImage(QtCore.QPoint(0, 0), self.image)
        qp.end()

    def setBBoxes(self, bboxes):
        self.bboxes = bboxes

    def contextMenuEvent(self, event) -> None:
        if self.bboxes is None or len(self.bboxes) == 0:
            return

        x, y = event.pos().x(), event.pos().y()

        objects = bboxes_in_position(self.bboxes, (x, y))
        print(objects)

        menu = QMenu(self)
        for item in objects:
            action = menu.addAction(item)
            action.triggered.connect(functools.partial(self.item_selected, item))

        menu.popup(QtGui.QCursor.pos())

    @pyqtSlot(str)
    def item_selected(self, item: str):
        self.container.item_selected(item)
