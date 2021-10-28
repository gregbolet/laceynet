from PyQt5.QtWidgets import *
from PyQt5 import QtGui
from PyQt5.QtCore import *
import sys, random

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("blah")
        self.setGeometry(100,100,600,400)
        self.UIComponents()
        self.show()

    def UIComponents(self):
        self.button = QPushButton("Click", self)
        self.button.setGeometry(200,150,100,300)
        self.button.clicked.connect(self.clickme)
        self.button.setText("Start")
        self.index = 0

    def clickme(self):
        list = [1,2,3,4,5 ,6,7 ,8,9]
        if self.index < len(list):
            self.button.setText(str(list[self.index]))
            self.index = self.index +1
        else:
            self.button.setText("Game over")
        print("rpessed")
    
App = QApplication(sys.argv)
window = Window()
sys.exit(App.exec())