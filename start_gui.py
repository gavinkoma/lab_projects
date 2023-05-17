from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont

def main():
	app = QApplication([])
	window = QWidget()
	window.setGeometry(100,100,200,300)
	window.setWindowTitle("My Simple GUI")


	layout = QVBoxLayout()

	label = QLabel("Push the button below")
	textbox = QTextEdit()
	button = QPushButton("Press me")

	button.clicked.connect(lambda: on_clicked(textbox.toPlainText()))


	layout.addWidget(label)
	layout.addWidget(textbox)
	layout.addWidget(button)

	window.setLayout(layout)
	window.show()
	app.exec_()



def on_clicked(msg):
	message = QMessageBox()
	message.setText(msg)
	message.exec_()



if __name__ == '__main__':
	main()