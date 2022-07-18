#!/usr/bin/python
import queue
import rospy
from kivymd.app import MDApp
from kivy.lang import Builder
from std_msgs.msg import Bool


#kivy convention is that you can name your kivy class literally anything you want but
#it must end with App for it to be /classified/
class TreadmillControlApp(MDApp):
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

    def start_tread(self,*args):
        print("Started Treadmill.")
        msg=True
        pub_start.publish(msg)
        

    def record_video(self,*args):
        print("Recording started.")
        msg=True
        pub_record.publish(msg)

    def stop_exit(self,*args):
        print("Quitting and exiting.")
        msg=True
        pub_exit.publish(msg)

    def speed_16(self,*args):
        print("Setting treadmill speed to 16.")
        msg=True
        pubsp16.publish(msg)

    def speed_20(self,*args):
        print("Setting treadmill speed to 20.")
        msg=True
        pubsp20.publish(msg)

    def speed_24(self,*args):
        print("Setting treadmill speed to 24.")
        msg=True
        pubsp24.publish(msg)

    def speed_28(self,*args):
        print("Setting treadmill speed to 28.")
        msg=True
        pubsp28.publish(msg)

    def speed_32(self,*args):
        print("Setting treadmill speed to 32.")
        msg=True
        pubsp32.publish(msg)


if __name__ == '__main__':
    #okay so we have 16, 20, 24, 28, 32 speeds and we need a button for every one of them
    #we also will need a button that simple starts and stops the treadmill
    #we could include a window for camera view but i havent a clue how to do that,
    #(and it feels complicated)
    pub_start=rospy.Publisher('/start_tread',Bool,queue_size=1)
    pub_record=rospy.Publisher('/record',Bool,queue_size=1)
    pub_exit=rospy.Publisher('/exit',Bool,queue_size=1)

    pubsp16=rospy.Publisher('sp16',Bool,queue_size=1)
    pubsp20=rospy.Publisher('sp20',Bool,queue_size=1)
    pubsp24=rospy.Publisher('sp24',Bool,queue_size=1)
    pubsp28=rospy.Publisher('sp28',Bool,queue_size=1)
    pubsp32=rospy.Publisher('sp32',Bool,queue_size=1)


    rospy.init_node('simple_gui', anonymous=True)

    TreadmillControlApp().run()





