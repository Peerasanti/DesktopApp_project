import sys
import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "1"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import tensorflow as tf
import cv2
from PyQt5.QtWidgets import ( QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, 
                             QStackedWidget, QPushButton, QFileDialog, QDialog, QHBoxLayout, 
                             QFormLayout, QLineEdit, QDialogButtonBox, QDesktopWidget )
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QIcon, QPixmap, QImage, QFont

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
    def __init__(self, stack, main_window):
        super().__init__()
        self.stack = stack
        self.main_window = main_window
        self.video_path = None
        self.cap = None  
        self.is_playing = False

        self.setFixedSize(650, 660)  

        # Header
        self.header = QLabel("🐭 Mice Detection Program")
        self.header.setAlignment(Qt.AlignCenter)
        self.header.setFont(QFont("Arial", 24))
        self.header.setObjectName("Header")

        # Video display
        self.label = QLabel("🎥 เลือกไฟล์วิดีโอหรือกล้อง")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFixedSize(600, 400)
        self.label.setObjectName("VideoDisplay")
        self.label.mousePressEvent = self.on_label_click

        # Status label
        self.status_label = QLabel("⏳ รอการเลือกวิดีโอหรือกล้อง")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFixedSize(580, 50)  
        self.status_label.move(10, 10)  
        self.status_label.raise_()

        # Buttons
        self.button = QPushButton("📂 เลือกไฟล์วิดีโอ")
        self.button.clicked.connect(self.browse_video)

        self.camera = QPushButton("📷 ตรวจจับด้วยกล้อง")
        self.camera.clicked.connect(self.use_camera)

        self.submit = QPushButton("✅ ยืนยัน")
        self.submit.clicked.connect(self.check_path)

        self.clear = QPushButton("❌ ล้างข้อมูล")
        self.clear.clicked.connect(self.clear_data)

        # Layout
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.button)
        btn_layout.addWidget(self.camera)

        action_layout = QHBoxLayout()
        action_layout.addWidget(self.submit)
        action_layout.addWidget(self.clear)

        center_layout = QVBoxLayout()
        center_layout.addWidget(self.label)
        center_layout.addWidget(self.status_label)
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
    
    def on_label_click(self, event):
        if self.cap and self.cap.isOpened():
            if self.is_playing:
                self.timer.stop()
                self.status_label.setText("⏸️ วิดีโอถูกหยุด")
            else:
                self.timer.start(30)
                self.status_label.setText("▶️วิดีโอกำลังเล่น")
            self.is_playing = not self.is_playing

    def browse_video(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "เลือกไฟล์วิดีโอ",
            "",
            "Video Files (*.mp4 *.avi *.mov *.mkv);;All Files (*)"
        )
        if file_path:
            valid_extensions = [".mp4", ".avi", ".mov", ".mkv"]
            ext = os.path.splitext(file_path)[1].lower()

            if ext not in valid_extensions:
                self.label.setText("❌ ไม่สามารถเปิดไฟล์วิดีโอนี้ได้")
                return

            self.start_capture(file_path)

    def use_camera(self):
        dialog = IPCameraDialog()
        if dialog.exec_() == QDialog.Accepted:
            ip = dialog.get_ip()
            self.start_capture(ip)

    def start_capture(self, source):
        if self.cap:
            self.cap.release()

        self.video_path = source
        self.cap = cv2.VideoCapture(source)
        if not self.cap.isOpened():
            self.label.setText("❌ ไม่สามารถเชื่อมต่อกล้องหรือเปิดวิดีโอได้")
            return

        self.is_playing = True
        self.timer.start(30)
        self.status_label.setText("▶️วิดีโอกำลังเล่น")

    def next_frame(self):
        if self.cap and self.is_playing:
            ret, frame = self.cap.read()
            if not ret:
                self.timer.stop()
                self.cap.release()
                self.label.setText("✅ จบวิดีโอหรือสัญญาณกล้องขาดหาย")
                return

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            qimg = QImage(frame.data, w, h, ch * w, QImage.Format_RGB888)
            margin = 10  
            size = self.label.size()
            scaled_size = QSize(size.width() - margin * 2, size.height() - margin * 2)
            pixmap = QPixmap.fromImage(qimg).scaled(
                scaled_size, Qt.IgnoreAspectRatio, Qt.SmoothTransformation
            )
            self.label.setPixmap(pixmap)
    
    def check_path(self):
        # if self.video_path:
        #     self.main_window.switch_to_page(1)
        # else:
        #     self.label.setText("❌ ยังไม่ได้เลือกไฟล์วิดีโอหรือกล้อง")
        #     return
        self.main_window.switch_to_page(1)

    def clear_data(self):
        if self.cap:
            self.cap.release()
        self.timer.stop()
        self.label.setText("🎥 เลือกไฟล์วิดีโอหรือกล้อง")
        self.status_label.setText("⏳ รอการเลือกวิดีโอหรือกล้อง")
        self.video_path = None
        self.cap = None

class PageTwo(QWidget):
    def __init__(self, stack, main_window):
        super().__init__()
        self.stack = stack
        self.main_window = main_window

        self.setFixedSize(1600, 900)  

        layout = QVBoxLayout()
        label = QLabel("This is Page Two")
        button = QPushButton("Go to Page One")
        button.clicked.connect(lambda: self.main_window.switch_to_page(0))
        layout.addWidget(label)
        layout.addWidget(button)
        layout.setAlignment(Qt.AlignCenter) 
        self.setLayout(layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("mice detection")
        self.setWindowIcon(QIcon("assets/mouse.png"))

        self.stack = QStackedWidget()

        self.page1 = PageOne(self.stack, self)
        self.page2 = PageTwo(self.stack, self)

        self.stack.addWidget(self.page1)
        self.stack.addWidget(self.page2)

        self.setCentralWidget(self.stack)

        self.setFixedSize(self.page1.size()) 

        self.center_window()  

    def switch_to_page(self, index):
        self.stack.setCurrentIndex(index)
        # อัปเดตขนาดหน้าต่างตามขนาดของหน้าใหม่
        current_widget = self.stack.currentWidget()
        self.setFixedSize(current_widget.size()) 
        self.center_window()  

    def center_window(self):
        window_rect = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        window_rect.moveCenter(center_point)
        self.move(window_rect.topLeft())  

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