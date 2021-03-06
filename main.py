import sys

import cv2
import numpy
import qimage2ndarray

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QFileDialog, QPushButton, QWidget, QHBoxLayout
from openni import openni2


class Window(QWidget):
    def __init__(self):
        super(Window, self).__init__()
        self.upbtn = QtWidgets.QPushButton('up')
        self.upbtn.clicked.connect(self.up_click)
        self.downbtn = QtWidgets.QPushButton('down')
        self.downbtn.clicked.connect(self.down_click)
        self.setWindowTitle("Player")
        self.setGeometry(100, 100, 600, 500)
        self.isPlay = False


        self.open = QPushButton("open")
        self.open.clicked.connect(self.file_dialog)

        self.play = QPushButton('pause')
        self.play.clicked.connect(self.play_video)

        self.slider = QtWidgets.QSlider(Qt.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.sliderMoved.connect(self.set_position)

        self.hboxTop = QHBoxLayout()
        self.hboxTop.addWidget(self.upbtn)
        self.hboxTop.addWidget(self.downbtn)

        self.hbox = QHBoxLayout()
        self.hbox.setContentsMargins(0, 0, 0, 0)

        self.hbox.addWidget(self.open)
        self.hbox.addWidget(self.play)
        self.hbox.addWidget(self.slider)

        self.labelColor = QtWidgets.QLabel()
        self.labelDepth = QtWidgets.QLabel()
        self.hboxLabels = QHBoxLayout()
        self.hboxLabels.addWidget(self.labelColor)
        self.hboxLabels.addWidget(self.labelDepth)

        self.vbox = QtWidgets.QVBoxLayout()
        self.vbox.addLayout(self.hboxTop)
        self.vbox.addLayout(self.hboxLabels)
        self.vbox.addLayout(self.hbox)

        self.setLayout(self.vbox)
        self.timer = QTimer()

        self.show()

    def up_click(self):
        self.slider.setValue(self.slider.value() + 1)
        self.set_position(self.slider.value())

    def down_click(self):
        self.slider.setValue(self.slider.value() - 1)
        self.set_position(self.slider.value())

    def play_video(self):
        if self.isPlay:
            self.timer.stop()
            self.play.setText('play')
            self.isPlay = False
        else:
            self.timer.start(40)
            self.play.setText('pause')
            self.isPlay = True

    def file_dialog(self):
        file = QFileDialog.getOpenFileName(self, "ONI *.oni")[0]

        if file == '':
            return

        if openni2.is_initialized():
            self.streamColor.stop()
            self.streamDepth.stop()
            openni2.unload()

        openni2.initialize()
        self.device = openni2.Device(str.encode(file))
        self.streamColor = self.device.create_color_stream()
        self.streamDepth = self.device.create_depth_stream()
        self.playback = openni2.PlaybackSupport(self.device)
        self.streamColor.start()
        self.streamDepth.start()
        self.slider.setRange(0, self.streamDepth.get_number_of_frames())
        self.playback.seek(self.streamColor, 0)
        self.playback.seek(self.streamDepth, 0)
        self.set_frame_depth()
        self.set_frame_color()
        self.timer.timeout.connect(self.slider_move)
        self.timer.start(40)
        self.isPlay = True
        self.play.setText('pause')

    def slider_move(self):
        self.slider.setValue(self.slider.value() + 1)
        self.set_position(self.slider.value())

    def set_frame_depth(self):
        frame = self.streamDepth.read_frame()
        numpyBuffer = numpy.frombuffer(frame.get_buffer_as_uint16(), dtype=numpy.uint16)
        magiс = numpyBuffer.reshape(frame.height, frame.width)
        img = cv2.convertScaleAbs(cv2.cvtColor(magiс, cv2.COLOR_BGR2RGB), alpha=(255.0/65535.0))
        image = qimage2ndarray.array2qimage(img)
        self.labelDepth.setPixmap(QPixmap.fromImage(image))

    def set_frame_color(self):
        frame = self.streamColor.read_frame()
        numpyBuffer = numpy.frombuffer(frame.get_buffer_as_uint8(), dtype=numpy.uint8)
        magiс = numpyBuffer.reshape(frame.height, frame.width, 3)
        img = cv2.cvtColor(magiс, cv2.COLOR_BGRA2BGR)
        image = qimage2ndarray.array2qimage(img)
        self.labelColor.setPixmap(QPixmap.fromImage(image))

    def set_position(self, position):
        self.playback.seek(self.streamColor, position)
        self.playback.seek(self.streamDepth, position)
        self.set_frame_color()
        self.set_frame_depth()


def application():
    app = QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec())


if __name__ == '__main__':
    application()







