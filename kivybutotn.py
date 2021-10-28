import kivy
kivy.require("1.9.1")
from kivy.app import App
from kivy.uix.button import Button
from kivy.properties import ListProperty


class ButtonApp(App):
    
    def build(self):
        self.btn = Button(text = 'Start!', font_size = '20sp', background_color = (1,1,1,1), color = (1,1,1,1), size = (32,32), size_hint =(.2,.2),pos=(300,250))
        self.btn.bind(on_press = self.callback)
        self.index = 0
        return self.btn

    def callback(self, number):
        self.btn.text = number
        print('button pressed')

list = [1,2,3,4,5,6,7,8,9]
root = ButtonApp()

root.mylist = list
print(root.mylist)
root.run()

