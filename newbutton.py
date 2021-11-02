from PyQt5.QtWidgets import *
from PyQt5 import QtGui
from PyQt5.QtCore import *
import sys, random

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Blockchain Guessing Game")
        self.UIComponents()
        self.showFullScreen()
        self.setUIGeometries()

    def setUIGeometries(self):
        self.button.setGeometry(0, 0,self.width()/2,self.height()/2)


    def UIComponents(self):
        self.button = QPushButton("Click ME!", self)
        self.button.clicked.connect(self.clickme)
        self.button.setText("Start")
        self.index = 0

    def clickme(self):
        list = [1,2,3,4,5,6,7,8,9]
        if self.index < len(list):
            self.button.setText(str(list[self.index]))
            self.index = self.index +1
        else:
            self.button.setText("Game over")
        print("pressed")
    
App = QApplication(sys.argv)
window = Window()
sys.exit(App.exec())