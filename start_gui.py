from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont

class MyGUI(QtWidgets.QDialog):
	
	def __init__(self):
		app = QApplication([])
		window = QWidget()
		window.setGeometry(100,100,200,300)
		window.setWindowTitle("Reaching Kinematics")


		layout = QVBoxLayout()

		label = QLabel("")
		textbox = QTextEdit()
		button = QPushButton("Dump Raw Files")

		button.clicked.connect(lambda: on_clicked(textbox.toPlainText()))


		layout.addWidget(label)
		layout.addWidget(textbox)
		layout.addWidget(button)

		window.setLayout(layout)
		window.show()
		app.exec_()



	def on_clicked(msg):
		message = QMessageBox()
		message.setText("Dumping Video Files...")
		message.exec_()



if __name__ == '__main__':
	main()

from PyQt5 import QtWidgets 

# It is considered a good tone to name classes in CamelCase.
class MyFirstGUI(QtWidgets.QDialog): 

    def __init__(self):
        # Initializing QDialog and locking the size at a certain value
        super(MyFirstGUI, self).__init__()
        self.setFixedSize(411, 247)

        # Defining our widgets and main layout
        self.layout = QtWidgets.QVBoxLayout(self)
        self.label = QtWidgets.QLabel("Hello, world!", self)
        self.buttonBox = QtWidgets.QDialogButtonBox(self) 
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)

        # Appending our widgets to the layout
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.buttonBox)

        # Connecting our 'OK' and 'Cancel' buttons to the corresponding return codes
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    gui = MyFirstGUI()
    gui.show()
    sys.exit(app.exec_())