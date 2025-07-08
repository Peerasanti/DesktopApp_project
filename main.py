import sys
import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "1"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import tensorflow as tf
import cv2
from PyQt5.QtWidgets import ( QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, 
                             QStackedWidget, QPushButton, QFileDialog, QDialog, QHBoxLayout, 
                             QFormLayout ) 
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QPixmap, QImage, QFont

import cv2
from PyQt5.QtWidgets import (
    QWidget, QPushButton, QLabel, QVBoxLayout,
    QFileDialog, QDialog, QLineEdit, QDialogButtonBox, QFormLayout
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap


class IPCameraDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("กรอก IP ของกล้อง")
        self.setFixedSize(500, 100)
        self.ip_input = QLineEdit(self)
        self.ip_input.setPlaceholderText("เช่น rtsp://admin:pass@192.168.1.64/stream1")

        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.button_box = QDialogButtonBox(buttons)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        layout = QFormLayout()
        layout.addRow("IP/URL กล้อง:", self.ip_input)
        layout.addWidget(self.button_box)
        self.setLayout(layout)

    def get_ip(self):
        return self.ip_input.text()


class PageOne(QWidget):
    def __init__(self, stack):
        super().__init__()

        self.stack = stack
        self.video_path = None
        self.cap = None

        # Header
        self.header = QLabel("🐭 Mice Detection Program")
        self.header.setAlignment(Qt.AlignCenter)
        self.header.setFont(QFont("Arial", 24))
        self.header.setObjectName("Header")

        # Video display
        self.label = QLabel("ยังไม่ได้เลือกไฟล์วิดีโอหรือกล้อง")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFixedSize(600, 400)
        self.label.setObjectName("VideoDisplay")

        # Buttons
        self.button = QPushButton("📂 เลือกไฟล์วิดีโอ")
        self.button.clicked.connect(self.browse_video)

        self.camera = QPushButton("📷 ตรวจจับด้วยกล้อง")
        self.camera.clicked.connect(self.use_camera)

        self.submit = QPushButton("✅ Submit")
        self.submit.clicked.connect(lambda: stack.setCurrentIndex(1))

        self.clear = QPushButton("❌ Clear")
        self.clear.clicked.connect(lambda: stack.setCurrentIndex(0))

        # Layout
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.button)
        btn_layout.addWidget(self.camera)

        action_layout = QHBoxLayout()
        action_layout.addWidget(self.submit)
        action_layout.addWidget(self.clear)

        center_layout = QVBoxLayout()
        center_layout.addWidget(self.label)
        center_layout.addLayout(btn_layout)
        center_layout.addLayout(action_layout)
        center_layout.setAlignment(Qt.AlignCenter)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.header)
        main_layout.addLayout(center_layout)
        main_layout.addStretch()

        self.setLayout(main_layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.next_frame)

    def browse_video(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "เลือกไฟล์วิดีโอ",
            "",
            "Video Files (*.mp4 *.avi *.mov *.mkv);;All Files (*)"
        )
        if file_path:
            self.start_capture(file_path)

    def use_camera(self):
        dialog = IPCameraDialog()
        if dialog.exec_() == QDialog.Accepted:
            ip = dialog.get_ip()
            self.start_capture(ip)

    def start_capture(self, source):
        if self.cap:
            self.cap.release()

        self.cap = cv2.VideoCapture(source)
        if not self.cap.isOpened():
            self.label.setText("❌ ไม่สามารถเชื่อมต่อกล้องหรือเปิดวิดีโอได้")
            return

        self.timer.start(30)

    def next_frame(self):
        if self.cap:
            ret, frame = self.cap.read()
            if not ret:
                self.timer.stop()
                self.cap.release()
                self.label.setText("✅ จบวิดีโอหรือสัญญาณกล้องหาย")
                return

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            qimg = QImage(frame.data, w, h, ch * w, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qimg).scaled(
                self.label.width(), self.label.height(), Qt.KeepAspectRatio
            )
            self.label.setPixmap(pixmap)


class PageTwo(QWidget):
    def __init__(self, stack):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel("This is Page Two")
        button = QPushButton("Go to Page One")
        button.clicked.connect(lambda: stack.setCurrentIndex(0))
        layout.addWidget(label)
        layout.addWidget(button)
        self.setLayout(layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("mice detection")
        self.setGeometry(200, 200, 600, 600)
        self.setWindowIcon(QIcon("assets/mouse.png"))

        self.stack = QStackedWidget()

        self.page1 = PageOne(self.stack)
        self.page2 = PageTwo(self.stack)

        self.stack.addWidget(self.page1)
        self.stack.addWidget(self.page2)

        self.setCentralWidget(self.stack)

def main():
    print(tf.__version__)
    app = QApplication(sys.argv)

    try:
        with open("main.qss", "r") as style_file:
            app.setStyleSheet(style_file.read())
    except FileNotFoundError:
        print("Error: style.qss file not found. Using default styling.")

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())



if __name__ == "__main__":
    main()