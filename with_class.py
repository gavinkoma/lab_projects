from PyQt5 import QtCore,QtGui,QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QMessageBox, QLineEdit
from PyQt5.QtGui import QPixmap


class Ui_MainWindow(object):
    def setupUi(self,MainWindow):
        #####main widget#####
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(600,650)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        #####image for cameras#####
        self.pixmap = QPixmap('cam.jpg')
        self.high_rez = QtCore.QSize(200,200)
        self.pixmap = self.pixmap.scaled(
            self.high_rez,
            aspectRatioMode=QtCore.Qt.KeepAspectRatio
            )


        #####boolean comment for camera 1#####
        self.label1 = QLabel("Camera 1 Status:",self.centralwidget)
        self.label1.move(120,20)
        self.label1.setObjectName("label1")
        self.label1.setStyleSheet("border: 2px solid black;")

        self.imagelabel1 = QLabel("",self.centralwidget)
        self.imagelabel1.setAlignment(QtCore.Qt.AlignCenter)
        self.imagelabel1.setPixmap(self.pixmap)
        self.imagelabel1.move(80, 80)

        

        #####boolean comment for camera 2#####
        self.label2 = QLabel("Camera 2 Status:",self.centralwidget)
        self.label2.move(360,20)
        self.label2.setObjectName("label2")
        self.label2.setStyleSheet("border: 2px solid black;")
        self.label2.setAlignment(QtCore.Qt.AlignCenter)

        self.imagelabel2 = QLabel("",self.centralwidget)
        self.imagelabel2.setAlignment(QtCore.Qt.AlignCenter)
        self.imagelabel2.setPixmap(self.pixmap)
        self.imagelabel2.move(320, 80)


        #####textbox info#####
        self.textbox = QLineEdit(self.centralwidget)
        self.textbox.move(80,190)
        self.textbox.resize(370,40)
        self.textbutton = QtWidgets.QPushButton(self.centralwidget)
        self.textbutton.setGeometry(QtCore.QRect(450,183,80,53))
        self.textbutton.setObjectName("textbutton")
        MainWindow.setCentralWidget(self.centralwidget)

        #####button for dumping videos#####
        self.button = QtWidgets.QPushButton(self.centralwidget)
        self.button.setGeometry(QtCore.QRect(80,250, 441, 161))
        self.button.setObjectName("button")
        self.button.setStyleSheet("background-color: plum")
        MainWindow.setCentralWidget(self.centralwidget)

        ##button for compressing videos automatically#####
        self.compressbutton = QtWidgets.QPushButton(self.centralwidget)
        self.compressbutton.setGeometry(QtCore.QRect(80,430, 441, 161))
        self.compressbutton.setObjectName("compressbutton")
        self.compressbutton.setStyleSheet("background-color: darksalmon")
        MainWindow.setCentralWidget(self.centralwidget)

        #####setting the menu bar#####
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0,0,800,21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)

        #####setting the status bar#####
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)


        #####button for dumping videos#####
        self.button.clicked.connect(self.show_pop)

        #####button for compressing videos#####
        self.compressbutton.clicked.connect(self.compress)

        #####textbox?#####
        self.textbutton.clicked.connect(self.text_click)


    def text_click(self):
        msg = QMessageBox()
        msg.setWindowTitle("Write to .txt")
        msg.setText("Written!")
        x = msg.exec_()


    def retranslateUi(self,MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow","Reaching Kinematics GUI"))
        self.button.setText(_translate("MainWindow","Dump Video Files!"))
        self.compressbutton.setText(_translate("MainWindow",'Compress Raw Avis?'))
        self.textbutton.setText(_translate("MainWindow","Write .txt"))

    def show_pop(self):
        msg = QMessageBox()
        msg.setWindowTitle("Dumping video files...")
        msg.setText("hold your horses cowboy...")
        x = msg.exec_()

    def compress(self):
        msg = QMessageBox()
        msg.setWindowTitle("Compress video files?")
        msg.setText("Please wait!")
        x = msg.exec_()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())