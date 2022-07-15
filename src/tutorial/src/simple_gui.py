#!/usr/bin/python

import rospy
from kivymd.app import MDApp
from kivy.lang import Builder


#kivy convention is that you can name your kivy class literally anything you want but
#it must end with App for it to be /classified/
class TutorialApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        #variable screen needs to know the filepath to our gui
        #so now our variable screen has been taken over by our provided file
        #there is a way to determine style of your file, but kivy seems to prefer having
        #a separate file that defines the style of the gui
        self.screen=Builder.load_file('/home/gavinkoma/simple_gui/src/tutorial/ros_gui.kv')

    #when we build our app, we access the screen variable
    def build(self):
        return self.screen

if __name__ == '__main__':

    rospy.init_node('simple_gui', anonymous=True)

    TutorialApp().run()





