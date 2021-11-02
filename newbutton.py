from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys, random

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Blockchain Guessing Game")
        self.UIComponents()
        self.showFullScreen()
        self.setUIGeometries()
        print(self.width(),self.height())

    def setUIGeometries(self):
        buttonWidth = 1000
        buttonHeight = 1000
        self.button.setGeometry(self.width()/2-buttonWidth/2,self.height()/2-buttonHeight/2,buttonWidth,buttonHeight)
        self.exitButton.setGeometry(100,100, 250,250)

    def UIComponents(self):
        self.button = QPushButton("Click ME!", self)
        self.exitButton = QPushButton("EXIT",self)
        self.button.setFont(QFont('Times', 45))
        self.button.clicked.connect(self.clickme)
        self.exitButton.clicked.connect(self.exit)
        self.button.setText("Start")

        self.index = 0

        grid_layout.addWidget(self.button, 0, 0)

    def clickme(self):
        list = [1,2,3,4,5,6,7,8,9]
        if self.index < len(list):
            self.button.setText(str(list[self.index]))
            self.index = self.index +1
        else:
            self.button.setText("Game over")
        print("pressed")

    def exit(self):
        sys.exit(App.exec())
    

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    window.showFullScreen()
    sys.exit(app.exec_())