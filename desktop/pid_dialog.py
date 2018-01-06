# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pid_controller.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QDialog


class Pid_Dialog(QDialog):
    def __init__(self):
        super(Pid_Dialog, self).__init__()
        self.dialog = Pid_Controller()
        self.dialog.setupUi(self)

    def get_values(self):
        result = self.exec_()

        try:
            kp_side = round(float(self.dialog.kp_side_edit.text()), 2)
        except:
            kp_side = 0
        try:
            ki_side = round(float(self.dialog.ki_side_edit.text()), 2)
        except:
            ki_side = 0
        try:
            kd_side = round(float(self.dialog.kd_side_edit.text()), 2)
        except:
            kd_side = 0

        try:
            kp_forward = round(float(self.dialog.kp_side_edit.text()), 2)
        except:
            kp_forward = 0
        try:
            ki_forward = round(float(self.dialog.ki_side_edit.text()), 2)
        except:
            ki_forward = 0
        try:
            kd_forward = round(float(self.dialog.kd_side_edit.text()), 2)
        except:
            kd_forward = 0

        return result, kp_forward, ki_forward, kd_forward, kp_side, ki_side, kd_side


class Pid_Controller:
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(665, 329)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(190, 280, 461, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.groupBox = QtWidgets.QGroupBox(Dialog)
        self.groupBox.setGeometry(QtCore.QRect(30, 30, 251, 221))
        self.groupBox.setObjectName("groupBox")
        self.label_8 = QtWidgets.QLabel(self.groupBox)
        self.label_8.setGeometry(QtCore.QRect(30, 40, 191, 17))
        self.label_8.setObjectName("label_8")
        self.label_7 = QtWidgets.QLabel(self.groupBox)
        self.label_7.setGeometry(QtCore.QRect(30, 90, 191, 17))
        self.label_7.setObjectName("label_7")
        self.label_9 = QtWidgets.QLabel(self.groupBox)
        self.label_9.setGeometry(QtCore.QRect(30, 140, 191, 17))
        self.label_9.setObjectName("label_9")

        self.groupBox_2 = QtWidgets.QGroupBox(Dialog)
        self.groupBox_2.setGeometry(QtCore.QRect(350, 30, 261, 221))
        self.groupBox_2.setObjectName("groupBox_2")
        self.label_12 = QtWidgets.QLabel(self.groupBox_2)
        self.label_12.setGeometry(QtCore.QRect(30, 40, 191, 17))
        self.label_12.setObjectName("label_12")
        self.label_10 = QtWidgets.QLabel(self.groupBox_2)
        self.label_10.setGeometry(QtCore.QRect(30, 90, 191, 17))
        self.label_10.setObjectName("label_10")
        self.label_11 = QtWidgets.QLabel(self.groupBox_2)
        self.label_11.setGeometry(QtCore.QRect(30, 140, 191, 17))
        self.label_11.setObjectName("label_11")

        self.kp_side_edit = QtWidgets.QLineEdit(self.groupBox)
        self.kp_side_edit.setGeometry(QtCore.QRect(30, 60, 193, 29))
        self.kp_side_edit.setObjectName("kp_side_edit")

        self.ki_side_edit = QtWidgets.QLineEdit(self.groupBox)
        self.ki_side_edit.setGeometry(QtCore.QRect(30, 110, 193, 29))
        self.ki_side_edit.setObjectName("ki_side_edit")

        self.kd_side_edit = QtWidgets.QLineEdit(self.groupBox)
        self.kd_side_edit.setGeometry(QtCore.QRect(30, 160, 193, 29))
        self.kd_side_edit.setObjectName("kd_side_edit")

        self.kp_forward_edit = QtWidgets.QLineEdit(self.groupBox_2)
        self.kp_forward_edit.setGeometry(QtCore.QRect(30, 60, 193, 29))
        self.kp_forward_edit.setObjectName("kp_forward_edit")

        self.ki_forward_edit = QtWidgets.QLineEdit(self.groupBox_2)
        self.ki_forward_edit.setGeometry(QtCore.QRect(30, 110, 193, 29))
        self.ki_forward_edit.setObjectName("ki_forward_edit")

        self.kd_forward_edit = QtWidgets.QLineEdit(self.groupBox_2)
        self.kd_forward_edit.setGeometry(QtCore.QRect(30, 160, 193, 29))
        self.kd_forward_edit.setObjectName("kd_forward_edit")

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "PID Parameters"))

        self.groupBox.setTitle(_translate("Dialog", "Left & Right Parameters"))
        self.label_8.setText(_translate("Dialog", "KP:"))
        self.kd_side_edit.setPlaceholderText(_translate("Dialog", "KD"))
        self.label_7.setText(_translate("Dialog", "KI:"))
        self.label_9.setText(_translate("Dialog", "KD:"))
        self.kp_side_edit.setPlaceholderText(_translate("Dialog", "KP"))
        self.ki_side_edit.setPlaceholderText(_translate("Dialog", "KI"))
        self.groupBox_2.setTitle(_translate("Dialog", "Forward & Backward Parameters"))
        self.label_12.setText(_translate("Dialog", "KP:"))
        self.label_10.setText(_translate("Dialog", "KI:"))
        self.kd_forward_edit.setPlaceholderText(_translate("Dialog", "KD"))
        self.label_11.setText(_translate("Dialog", "KD:"))
        self.kp_forward_edit.setPlaceholderText(_translate("Dialog", "KP"))
        self.ki_forward_edit.setPlaceholderText(_translate("Dialog", "KI"))

        self.kp_side_edit.setText("1")
        self.ki_side_edit.setText("0")
        self.kd_side_edit.setText("0.5")
        self.kp_forward_edit.setText("0.5")
        self.ki_forward_edit.setText("0")
        self.kd_forward_edit.setText("0.5")
