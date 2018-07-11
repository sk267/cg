from PySide2 import QtCore, QtWidgets
import os
import maya.OpenMayaUI as mui
import shiboken2
import pymel.core as pm
from cg.system.renamer import hash_to_number
import time


class GuiTest(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(GuiTest, self).__init__(parent)

        nameLabel = QtWidgets.QLabel("Name Pattern")
        self.nameLine = QtWidgets.QLineEdit()

        self.addButton = QtWidgets.QPushButton("Rename!")
        self.addButton.show()
        self.addButton.clicked.connect(self.rename)

        self.resultDisplayOne = QtWidgets.QLabel("")
        self.resultDisplayTwo = QtWidgets.QLabel("")
        self.resultDisplayPoints = QtWidgets.QLabel("...")


# PySide.QtGui.QGridLayout.addLayout(arg__1, row, column, rowSpan, columnSpan[, alignment=0])
        mainLayout = QtWidgets.QGridLayout()

        fistRowLayout = QtWidgets.QHBoxLayout()
        fistRowLayout.addWidget(nameLabel)
        fistRowLayout.addWidget(self.nameLine)
        fistRowLayout.addWidget(self.addButton)
        mainLayout.addLayout(fistRowLayout, 1, 1)

        secondRowLayout = QtWidgets.QHBoxLayout()
        secondRowLayout.addWidget(self.resultDisplayOne)
        secondRowLayout.addWidget(self.resultDisplayPoints)
        secondRowLayout.addWidget(self.resultDisplayTwo)
        mainLayout.addLayout(secondRowLayout, 2, 1)

        self.setLayout(mainLayout)
        self.nameLine.textChanged.connect(self.textGeaendert)

    def rename(self, *args):
        name = hash_to_number(self.nameLine.text())
        hand_selection = pm.selected()
        for i in hand_selection:
            i.rename(next(name))

    def textGeaendert(self, *args):
        names = []
        if '#' in self.nameLine.text():
            name = hash_to_number(self.nameLine.text())
            hand_selection = pm.selected()
            
            for i in hand_selection:
                names.append(next(name))
            self.resultDisplayOne.setText(names[0])
            self.resultDisplayTwo.setText(names[-1])



pointer = mui.MQtUtil.mainWindow()
window = QtWidgets.QMainWindow(shiboken2.wrapInstance(long(pointer), QtWidgets.QWidget))
window.setCentralWidget(GuiTest())
window.show()
