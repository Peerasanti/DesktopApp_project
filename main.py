# Full path for run script: "C:\Users\WINDOWS\miniconda3\envs\rat_lab\python.exe" -u "d:\DesktopApp_project\main.py"

import sys
import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "1"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

# import warnings
# warnings.filterwarnings("ignore", category=DeprecationWarning)

import csv
import tensorflow as tf
import pandas as pd
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt

import seaborn as sns
from openpyxl import Workbook
from openpyxl.worksheet.worksheet import Worksheet
import cv2
import re
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import ( QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, 
                             QStackedWidget, QPushButton, QFileDialog, QDialog, QHBoxLayout, 
                             QFormLayout, QLineEdit, QDialogButtonBox, QDesktopWidget, QInputDialog,
                             QColorDialog, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
                             QComboBox, QTextEdit, QGridLayout, QFrame)
from PyQt5.QtCore import Qt, QTimer, QSize, QDateTime, QLocale
from PyQt5.QtGui import QIcon, QPixmap, QImage, QFont, QColor, QPainter
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from db import DatabaseManager 

class IPCameraDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("กรอก IP ของกล้องหรือ Webcam")
        self.setFixedSize(500, 120)
        self.ip_input = QLineEdit(self)
        self.ip_input.setPlaceholderText("เช่น rtsp://admin:pass@192.168.1.64/stream1")

        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.button_box = QDialogButtonBox(buttons)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.button_box.button(QDialogButtonBox.Ok).setObjectName("GreenButton")
        self.button_box.button(QDialogButtonBox.Cancel).setObjectName("RedButton")

        layout = QFormLayout()
        layout.addRow("IP/URL กล้องหรือ Webcam:", self.ip_input)
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
        self.setFixedSize(630, 670)  

        # Header
        self.header = QLabel("Mice Detection Program")
        self.header.setAlignment(Qt.AlignCenter)
        self.header.setFont(QFont("Arial", 26, QFont.Bold))
        self.header.setObjectName("Header")

        # Video / Camera Display
        self.label = QLabel("เลือกไฟล์วิดีโอหรือกล้อง")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFixedSize(600, 400)
        self.label.setObjectName("VideoDisplay")
        self.label.mousePressEvent = self.on_label_click

        # Status Label
        self.status_label = QLabel("⏳ รอการเลือกวิดีโอหรือกล้อง")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setObjectName("StatusLabel")

        # Buttons
        self.button = QPushButton("เลือกไฟล์วิดีโอ")
        self.button.clicked.connect(self.browse_video)
        self.button.setObjectName("YellowButton")

        self.camera = QPushButton("ตรวจจับด้วยกล้อง")
        self.camera.clicked.connect(self.use_camera)
        self.camera.setObjectName("YellowButton")

        self.submit = QPushButton("เริ่มทดลอง")
        self.submit.clicked.connect(self.show_experiment_setup)
        self.submit.setObjectName("GreenButton")

        self.clear = QPushButton("ล้างข้อมูล")
        self.clear.clicked.connect(self.clear_data)
        self.clear.setObjectName("RedButton")

        self.switch_page = QPushButton("ไปยังหน้าสรุปข้อมูล")
        self.switch_page.clicked.connect(self.switch_to_summary_page)
        self.switch_page.setObjectName("MainButton")

        self.theme_dropdown = QComboBox()
        self.theme_dropdown.setFixedSize(180, 32)
        self.theme_dropdown.setObjectName("ThemeDropdown")

        self.theme_dropdown.addItem("🌞 Light Theme", "light")
        self.theme_dropdown.addItem("🌜 Dark Theme", "dark")
        self.theme_dropdown.addItem("🌸 Pastel Theme", "pastel")
        self.theme_dropdown.addItem("🌈 Default Theme", "default")

        current_index = self.theme_dropdown.findData(self.main_window.get_theme())
        if current_index != -1:
            self.theme_dropdown.setCurrentIndex(current_index)

        self.theme_dropdown.currentIndexChanged.connect(self.change_theme)

        # Layouts
        header_layout = QHBoxLayout()
        header_layout.addWidget(self.header)
        header_layout.addStretch() 
        header_layout.addWidget(self.theme_dropdown)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.button)
        btn_layout.addWidget(self.camera)

        action_layout = QHBoxLayout()
        action_layout.addWidget(self.submit)
        action_layout.addWidget(self.clear)
        action_layout.addWidget(self.switch_page)

        center_layout = QVBoxLayout()
        center_layout.addWidget(self.label)
        center_layout.addWidget(self.status_label)
        center_layout.addSpacing(10)
        center_layout.addLayout(btn_layout)
        center_layout.addSpacing(15)
        center_layout.addLayout(action_layout)
        center_layout.setAlignment(Qt.AlignCenter)

        main_layout = QVBoxLayout()
        main_layout.addLayout(header_layout)  
        main_layout.addLayout(center_layout)
        main_layout.addStretch()
        self.setLayout(main_layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.next_frame)
    
    def update_theme_dropdown(self):
        current_theme = self.main_window.get_theme()
        index = self.theme_dropdown.findData(current_theme)
        if index != -1:
            self.theme_dropdown.blockSignals(True)
            self.theme_dropdown.setCurrentIndex(index)
            self.theme_dropdown.blockSignals(False)

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
            try:
                source = int(ip) 
            except ValueError:
                source = ip  
            self.start_capture(source)

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
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        if self.fps == 0 or np.isnan(self.fps):  
            self.fps = 30

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

            fps_text = f"FPS: {self.fps:.1f}"
            painter = QPainter(qimg)
            painter.setPen(QColor(0, 255, 128))  
            font = QFont("Segoe UI", 28, QFont.Bold)
            painter.setFont(font)
            painter.drawText(20, 70, fps_text)
            painter.end()

            margin = 10  
            size = self.label.size()
            scaled_size = QSize(size.width() - margin * 2, size.height() - margin * 2)
            
            pixmap = QPixmap.fromImage(qimg).scaled(
                scaled_size, Qt.IgnoreAspectRatio, Qt.SmoothTransformation
            )

            self.label.setPixmap(pixmap)

    def show_experiment_setup(self):
        if self.video_path is None:
            self.label.setText("❌ ยังไม่ได้เลือกไฟล์วิดีโอหรือกล้อง")
            return

        dialog = ExperimentSetupDialog(self.main_window.db, self)
        if dialog.exec_() == QDialog.Accepted:
            experiment_type_id, name, date, detail = dialog.get_experiment_data()
            if experiment_type_id == 0:
                QMessageBox.warning(self, "ข้อผิดพลาด", "กรุณาเลือกประเภทการทดลอง!")
                return
            experiment_id = self.main_window.db.add_experiment(experiment_type_id, name, date, detail if detail is not None else "ไม่มีรายละเอียดการทดลอง", self.video_path)
            if experiment_id:
                self.main_window.set_experiment_name(name)
                self.main_window.set_experiment_id(experiment_id)
                self.main_window.set_fps(self.fps)
                self.main_window.set_video_path(self.video_path)
                self.main_window.switch_to_page(1)
                self.clear_data()
            else:
                QMessageBox.warning(self, "ข้อผิดพลาด", "ไม่สามารถบันทึกการทดลองได้ กรุณาลองใหม่!")
        else:
            self.label.setText("🎥 เลือกไฟล์วิดีโอหรือกล้อง")
    
    def change_theme(self, index):
        theme = self.theme_dropdown.itemData(index)
        if theme:
            self.main_window.set_theme(theme)
            self.main_window.load_theme(theme)

    def clear_data(self):
        if self.cap:
            self.cap.release()
        self.timer.stop()
        self.label.setText("🎥 เลือกไฟล์วิดีโอหรือกล้อง")
        self.status_label.setText("⏳ รอการเลือกวิดีโอหรือกล้อง")
        self.video_path = None
        self.cap = None
        self.is_playing = False

    def switch_to_summary_page(self):
        self.clear_data()
        self.main_window.switch_to_page(2)



class ExperimentSetupDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("ตั้งค่าการทดลอง")
        self.setModal(True)  
        self.setFixedSize(550, 400)

        self.name_input = QLineEdit(self)
        self.date_input = QLineEdit(self)
        self.date_input.setText(
            QLocale(QLocale.English).toString(
                QDateTime.currentDateTime(), "yyyy-MM-dd HH:mm:ss"
            )
        )
        self.type_combo = QComboBox(self)
        self.detail = QTextEdit(self)
        self.detail.setFixedHeight(80)

        experiment_types = self.db.get_experiment_types()
        self.type_combo.addItem("เลือกประเภทการทดลอง", 0)
        for type_id, type_name in experiment_types:
            self.type_combo.addItem(type_name, type_id)

        layout = QFormLayout()
        layout.addRow("วันที่:", self.date_input)
        layout.addRow("ชื่อการทดลอง:", self.name_input)
        layout.addRow("ประเภทการทดลอง:", self.type_combo)
        layout.addRow("รายละเอียดการทดลอง:", self.detail)

        button_layout = QHBoxLayout()
        ok_button = QPushButton("ยืนยัน")
        ok_button.setObjectName("GreenButton")
        cancel_button = QPushButton("ยกเลิก")
        cancel_button.setObjectName("RedButton")
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

        ok_button.clicked.connect(self.validate_and_accept)
        cancel_button.clicked.connect(self.reject)

    def validate_and_accept(self):
        name = self.name_input.text().strip()
        experiment_type_id = self.type_combo.currentData()
        if not name:
            QMessageBox.warning(self, "ข้อมูลไม่ครบ", "กรุณากรอกชื่อการทดลองก่อนกด ยืนยัน")
            return
        
        elif experiment_type_id == 0:
            QMessageBox.warning(self, "ข้อมูลไม่ครบ", "กรุณาเลือกประเภทการทดลองก่อนกด ยืนยัน")
            return
        self.accept()

    def get_experiment_data(self):
        experiment_type_id = self.type_combo.currentData()
        name = self.name_input.text()
        date = self.date_input.text()
        detail = self.detail.toPlainText()
        if not name: 
            raise ValueError("ชื่อการทดลองต้องไม่ว่าง")
        return experiment_type_id, name, date, detail



class PageTwo(QWidget):
    def __init__(self, stack, main_window):
        super().__init__()
        self.stack = stack
        self.main_window = main_window
        self.setFocusPolicy(Qt.StrongFocus)
        self.move_mode = False
        self.is_camera = False
        self.setFixedSize(1400, 950)

        self.is_playing = False
        self.cap = None
        self.last_frame = None
        self.frame_count = 0
        self.process_every_n = 3
        self.hide_ui = False
        self.hide_detail_notes = True

        self.model = tf.keras.models.load_model("model/model_for_rat_V2.keras", safe_mode=False)
        self.polygon_manager = PolygonManager()
        self.drawing_polygon = False
        self.active_started = False
        self.mouse_pos = None
        self.polygon_name = ""
        self.polygon_color = (0, 255, 0)
        self.raw_data = []

        self.video_label = QLabel("📹 เริ่มการตรวจตำแหน่ง")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setObjectName("VideoDisplay")
        self.video_label.mousePressEvent = self.polygon_draw

        self.create_polygon_table()

        self.back_button = QPushButton("ย้อนกลับ")
        self.back_button.clicked.connect(self.on_back_button_clicked)
        self.back_button.setObjectName("YellowButton")

        self.summary_button = QPushButton("สรุปผล")
        self.summary_button.clicked.connect(self.submit_summary)
        self.summary_button.setObjectName("GreenButton")
        

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.polygon_table)
        button_layout.addWidget(self.back_button)
        button_layout.addWidget(self.summary_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.video_label, stretch=3)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.next_frame)

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Z and not self.drawing_polygon:
            self.start_drawing()
            self.next_frame()
        elif key == Qt.Key_Space:
            self.on_label_click()
        elif key == Qt.Key_H:
            self.hide_ui = not self.hide_ui
            self.next_frame()
        elif key == Qt.Key_M:
            if not self.drawing_polygon:
                self.move_polygon()
        elif key == Qt.Key_N:
            self.change_experiment_name()
        elif key == Qt.Key_X:
            self.clear_all_data()
            self.next_frame()
            self.update_polygon_table()
        elif key == Qt.Key_V:
            self.hide_detail_notes = not self.hide_detail_notes
            self.next_frame()
        elif self.move_mode:
            move_distance = 15
            if key == Qt.Key_W:
                self.polygon_manager.move_all_polygons(0, -move_distance)
            elif key == Qt.Key_S:
                self.polygon_manager.move_all_polygons(0, move_distance)
            elif key == Qt.Key_A:
                self.polygon_manager.move_all_polygons(-move_distance, 0)
            elif key == Qt.Key_D:
                self.polygon_manager.move_all_polygons(move_distance, 0)
            elif key == Qt.Key_Q:
                self.polygon_manager.rotate_all_polygons(np.deg2rad(5))
            elif key == Qt.Key_E:
                self.polygon_manager.rotate_all_polygons(np.deg2rad(-5))
            self.next_frame()
        else:
            super().keyPressEvent(event)
    
    def change_experiment_name(self):
        self.experiment_name, ok = QInputDialog.getText(self, "แก้ไขรหัสการทดลอง", "กรุณาตั้งรหัส", text=self.experiment_name)
        if not ok or not self.experiment_name.strip():
            return
        experiment_id = self.experiment_id  
        if self.main_window.db.update_experiment_name(experiment_id, self.experiment_name):
            return
        
    def clear_all_data(self):
        self.polygon_manager.polygons = {}

    def move_polygon(self):
        self.move_mode = not self.move_mode

    def delete_polygon(self, name):
        if name in self.polygon_manager.polygons:
            del self.polygon_manager.polygons[name]

    def edit_polygon(self, name):
        polygon = self.polygon_manager.polygons.get(name)
        if not polygon:
            return

        new_name, ok = QInputDialog.getText(self, "แก้ไขชื่อพื้นที่", "กรุณาตั้งชื่อใหม่", text=polygon.name)
        if not ok or not new_name.strip():
            return

        new_color = QColorDialog.getColor(QColor(polygon.color[2], polygon.color[1], polygon.color[0]), self)
        if not new_color.isValid():
            return

        if new_name != name:
            self.polygon_manager.polygons[new_name] = self.polygon_manager.polygons.pop(name)
            polygon.name = new_name

        polygon.color = (new_color.blue(), new_color.green(), new_color.red())

    def update_polygon_table(self):
        polygons = self.polygon_manager.polygons
        self.polygon_table.setRowCount(len(polygons))

        for i, (name, polygon) in enumerate(polygons.items()):
            name_item = QTableWidgetItem(name)
            color_item = QTableWidgetItem()
            hit_count_item = QTableWidgetItem(str(polygon.hit_count))
            hit_time_item = QTableWidgetItem(str(round(polygon.hit_time, 2)) + " วินาที")

            color = polygon.color
            rgb_color = (color[2], color[1], color[0])
            qcolor = QColor(*rgb_color)
            color_item.setBackground(qcolor)
            color_item.setText(f"({color[2]}, {color[1]}, {color[0]})")

            btn_delete = QPushButton("🗑️ ลบ")
            btn_delete.setStyleSheet("""background-color: #e74c3c; """)
            btn_delete.clicked.connect(lambda _, name=name: self.delete_polygon(name))

            btn_edit = QPushButton("✏️แก้ไข")
            btn_edit.setStyleSheet("""background-color: #f1c40f; """)
            btn_edit.clicked.connect(lambda _, name=name: self.edit_polygon(name))

            cell_widget = QWidget()
            layout = QHBoxLayout(cell_widget)
            layout.addWidget(btn_delete)
            layout.addWidget(btn_edit)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setAlignment(Qt.AlignCenter)
            cell_widget.setLayout(layout)

            self.polygon_table.setItem(i, 0, name_item)
            self.polygon_table.setItem(i, 1, color_item)
            self.polygon_table.setItem(i, 2, hit_count_item)
            self.polygon_table.setItem(i, 3, hit_time_item)
            self.polygon_table.setCellWidget(i, 4, cell_widget)

    def create_polygon_table(self):
        self.polygon_table = QTableWidget()
        self.polygon_table.setColumnCount(5)
        self.polygon_table.setHorizontalHeaderLabels(["ชื่อ Polygon", "สี", "จำนวนครั้ง", "เวลาทั้งหมด", "การจัดการ"])
        
        self.polygon_table.verticalHeader().setDefaultSectionSize(50)

        header = self.polygon_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        self.polygon_table.setFixedHeight(220)
        self.polygon_table.setEditTriggers(QTableWidget.NoEditTriggers)

        font = self.polygon_table.font()
        font.setPointSize(8)
        self.polygon_table.setFont(font)

        self.update_polygon_table()

    def stop_video(self):
        self.timer.stop()
        self.clear_all_data()
        if self.cap:
            self.cap.release()
            self.cap = None
        self.is_playing = False

    def on_back_button_clicked(self):
        self.stop_video()
        self.clear_all_data()
        self.main_window.db.delete_area_summary_by_experiment_id(self.experiment_id)
        self.main_window.db.delete_experiment_by_id(self.experiment_id)
        self.main_window.set_experiment_id(None)
        self.main_window.switch_to_page(0)

    def is_ip_camera(self):
        path = self.video_path
        if isinstance(path, int):
            return True
        elif isinstance(path, str):
            return (path.startswith("rtsp://") or 
                    path.startswith("http://") or 
                    path.startswith("https://") or 
                    path.startswith("/dev/video"))
        else:
            return False

    def update_video(self):
        self.experiment_name = self.main_window.get_experiment_name()
        self.experiment_id = self.main_window.get_experiment_id()
        self.experiment_note = self.main_window.db.get_experiment_note_by_id(self.experiment_id)
        self.fps = self.main_window.get_fps()
        self.video_path = self.main_window.get_video_path()
        if self.video_path is not None:
            if self.cap:
                self.cap.release()
            self.cap = cv2.VideoCapture(self.video_path)
            if not self.cap.isOpened():
                print("Error: ไม่สามารถเปิดวิดีโอจาก Path นี้ได้")
                self.cap = None
                return
            
            self.is_camera = self.is_ip_camera()
            
            if self.is_camera:
                self.is_playing = True
                self.timer.start(30)
            else:
                self.is_playing = True
                self.next_frame()
                self.timer.start(30)
        else:
            print("Warning: video_path is None")

    def on_label_click(self):
        if self.cap and self.cap.isOpened():
            if self.is_playing:
                self.timer.stop()
            else:
                self.timer.start(30)
            self.is_playing = not self.is_playing

    def next_frame(self):
        if not self.cap:
            return
        
        if not self.is_playing:
            if self.last_frame is None:
                success, frame = self.cap.read()
                if not success:
                    return
                self.last_frame = frame
            current_frame = self.last_frame
        else:
            ret, frame = self.cap.read()
            if not ret:
                self.timer.stop()
                self.cap.release()
                self.is_playing = False
                return
            self.last_frame = frame
            self.frame_count += 1
            if self.frame_count % self.process_every_n != 0:
                return
            current_frame = frame

        margin = 10
        size = self.video_label.size()
        scaled_size = QSize(size.width() - margin * 2, size.height() - margin * 2)
        frame_display = cv2.resize(current_frame, (scaled_size.width(), scaled_size.height()), interpolation=cv2.INTER_CUBIC)

        input_frame = cv2.resize(current_frame, (128, 128), interpolation=cv2.INTER_CUBIC)
        input_frame = np.expand_dims(input_frame, axis=0)
        result = self.model.predict(input_frame)[0]
        result = (result * 255).astype(np.uint8)
        mask = cv2.resize(result, (scaled_size.width(), scaled_size.height()), interpolation=cv2.INTER_CUBIC)
        _, binary_mask = cv2.threshold(mask, 100, 255, cv2.THRESH_BINARY)

        contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        center = None
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            M = cv2.moments(largest_contour)
            if M["m00"] != 0:  
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                center = (cX, cY)
                cv2.circle(frame_display, center, 5, (0, 0, 255), -1)

        green_layer = np.zeros((mask.shape[0], mask.shape[1], 3), dtype=np.uint8)
        green_layer[:, :] = (0, 255, 0)
        green_masked = cv2.bitwise_and(green_layer, green_layer, mask=binary_mask)

        frame_display = frame_display.astype(np.uint8)
        overlay_frame = cv2.addWeighted(frame_display, 0.9, green_masked, 0.5, 0)

        self.polygon_manager.draw_all(overlay_frame)

        self.calculate_overlap(binary_mask, center)
        if self.frame_count % int(self.fps) == 0:
            self.update_polygon_table()

        overlay_frame = cv2.cvtColor(overlay_frame, cv2.COLOR_BGR2RGB)
        h, w, ch = overlay_frame.shape
        qimg = QImage(overlay_frame.data, w, h, ch * w, QImage.Format_RGB888)

        painter = QPainter(qimg)
        match self.main_window.current_theme:
            case "dark":
                painter.setPen(QColor(0, 255, 128))
            case "light":
                painter.setPen(QColor(0, 128, 255))
            case "pastel":
                painter.setPen(QColor(255, 0, 128))
            case "default":
                painter.setPen(QColor(200, 200, 200)) 
            case _:
                painter.setPen(QColor(200, 200, 200))  
        font = QFont("Segoe UI", 14)
        painter.setFont(font)
        format_time = f"Time: {self.format_time()}"
        if not self.hide_ui:
            painter.drawText(10, 60, f"ID name: {self.experiment_name}")
            painter.drawText(10, 110, f"FPS: {self.fps:.1f}")
            painter.drawText(10, 140, format_time)
            painter.drawText(10, 170, f"(Space) Play/Pause")
            painter.drawText(10, 200, f"(Z) Draw Mode")
            painter.drawText(10, 230, f"(M) Move Mode")
            painter.drawText(10, 260, f"(N) Change Experiment ID")
            painter.drawText(10, 290, f"(H) Hide UI")
            painter.drawText(10, 320, f"(V) View Detail Notes")
            painter.drawText(10, 350, f"(X) Clear All!")
            if self.move_mode:
                painter.drawText(10, 420, f"Moving Polygon ...")
                painter.drawText(10, 450, f"(W, A, S, D) to Move")
                painter.drawText(10, 480, f"(Q, E) to Rotate")
            elif self.drawing_polygon:
                painter.drawText(10, 420, f"Drawing Polygon ...")
                painter.drawText(10, 450, f"(Left Click) to Draw")
                painter.drawText(10, 480, f"(Right Click) to Close")
            
            if not self.hide_detail_notes:
                painter.drawText(10, 520, f"Detail Notes:")
                painter.drawText(10, 550, f"{self.experiment_note}")

        painter.end()

        pixmap = QPixmap.fromImage(qimg).scaled(
            scaled_size, Qt.IgnoreAspectRatio, Qt.SmoothTransformation
        )

        self.video_label.setPixmap(pixmap)
    
    def format_time(self):
        seconds = int(self.frame_count // self.fps)
        minutes = seconds // 60  
        remaining_seconds = seconds % 60  
        return f"{minutes}:{remaining_seconds:02d}"

    def start_drawing(self):
        name, ok = QInputDialog.getText(self, "ชื่อพื้นที่", "กรุณาตั้งชื่อ")
        if not ok:
            return
        elif not name.strip():
            name = f"Polygon-{len(self.polygon_manager.polygons) + 1}"

        color = QColorDialog.getColor()
        if not color.isValid():
            return
        
        self.drawing_polygon = True
        self.active_started = False
        self.polygon_name = name
        self.polygon_color = (color.blue(), color.green(), color.red())

    def polygon_draw(self, event):
        pos = event.pos()
        x, y = pos.x(), pos.y()

        if event.button() == Qt.RightButton and self.drawing_polygon:
            self.polygon_manager.close_active()
            self.drawing_polygon = False
            self.active_started = False
            self.polygon_name = ""
            self.polygon_color = (0, 255, 0)

            if self.polygon_manager.active_polygon:  
                polygon = self.polygon_manager.active_polygon
                experiment_id = self.experiment_id
                area_points = str(polygon.points)  
                color_str = str(polygon.color) 

                polygon_id = self.main_window.db.save_area_summary(experiment_id, polygon.name, color_str, polygon.hit_count, polygon.hit_time, area_points)
                if polygon_id is not None:
                    print(f"Polygon saved with ID: {polygon_id} Name : {polygon.name}")
                    polygon.id = polygon_id
            self.next_frame()
            self.update_polygon_table()
            return

        if event.button() == Qt.LeftButton:
            if self.drawing_polygon:
                if not self.active_started:
                    name = self.polygon_name
                    color = self.polygon_color
                    self.polygon_manager.new_polygon(name, color)
                    self.active_started = True
                self.polygon_manager.add_point_to_active((x, y))
                self.next_frame()

    def calculate_overlap(self, binary_mask, center):
        experiment_id = self.experiment_id
        best_area_id = None
        best_area_name = None  
        best_intersect_ratio = 0.0

        for polygon in self.polygon_manager.polygons.values():
            if not polygon.is_closed:
                continue

            mask_area = np.count_nonzero(binary_mask)
            if mask_area == 0:
                polygon.is_inside = False
                continue

            poly_mask = np.zeros(binary_mask.shape, dtype=np.uint8)
            cv2.fillPoly(poly_mask, [np.array(polygon.points, dtype=np.int32)], 255)
            intersect_mask = cv2.bitwise_and(binary_mask, poly_mask)
            intersect_area = np.count_nonzero(intersect_mask)
            intersect_ratio = intersect_area / mask_area

            if intersect_ratio >= 0.7:
                if not polygon.is_inside:
                    polygon.hit_count += 1
                    polygon.is_inside = True
                if self.fps > 0:
                    polygon.hit_time += self.process_every_n / self.fps
                if intersect_ratio > best_intersect_ratio:
                    best_intersect_ratio = intersect_ratio
                    best_area_id = polygon.id
                    best_area_name = polygon.name  
            elif intersect_ratio >= 0.6 and polygon.is_inside:
                if self.fps > 0:
                    polygon.hit_time += self.process_every_n / self.fps
                if intersect_ratio > best_intersect_ratio:
                    best_intersect_ratio = intersect_ratio
                    best_area_id = polygon.id
                    best_area_name = polygon.name  
            else:
                polygon.is_inside = False

        if center:
            time_stamp = round(self.frame_count / self.fps, 1)
            self.raw_data.append({
                'experiment_id': experiment_id,
                'area_id': best_area_id,
                'time_stamp': time_stamp,
                'frame_count': self.frame_count,
                'area_name': best_area_name,  
                'rat_position_x': center[0],
                'rat_position_y': center[1]
            })
    
    def submit_summary(self):
        
        reply = QMessageBox.question(self, "ยืนยันการจบการทดลอง", 
                                     "คุณต้องการจบการทดลองและบันทึกข้อมูลหรือไม่?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            for polygon in self.polygon_manager.polygons.values():
                if polygon.id is not None:  
                    success = self.main_window.db.update_area_summary(polygon.id, polygon.name, str(polygon.color), polygon.hit_count, round(polygon.hit_time, 2), str(polygon.points))
                    if not success:
                        print(f"ไม่สามารถอัปเดตข้อมูล polygon {polygon.name} (ID: {polygon.id})")
            
            if self.raw_data:
                data_to_insert = [
                    (d['experiment_id'], d['area_id'] if d['area_id'] is not None else None, d['time_stamp'], d['frame_count'], d['area_name'] if d['area_name'] is not None else None, d['rat_position_x'], d['rat_position_y'])
                    for d in self.raw_data
                ]
                success = self.main_window.db.save_raw_data_batch(data_to_insert)
                if not success:
                    QMessageBox.warning(self, "ข้อผิดพลาด", "ไม่สามารถบันทึก raw data ได้")
                self.raw_data = []

            self.stop_video()
            self.main_window.switch_to_page(2)
        else:
            pass



class Polygon:
    def __init__(self, name, color):
        self.id = None
        self.points = []
        self.color = color
        self.name = name
        self.is_closed = False
        self.hit_count = 0
        self.hit_time = 0
        self.is_inside = False
    
    def add_point(self, point):
        if not self.is_closed:
            self.points.append(point)
    
    def close(self):
        if len(self.points) >= 3:
            self.is_closed = True
    
    def draw(self, frame, thickness=2):
        if len(self.points) >= 2:
            pts = np.array(self.points, dtype=np.int32)
            cv2.polylines(frame, [pts], isClosed=self.is_closed, color=self.color, thickness=thickness)
        for x, y in self.points:
            cv2.circle(frame, (int(x), int(y)), 3, (255, 0, 0), -1)
        if self.points:
            cv2.putText(frame, self.name, (int(self.points[0][0]), int(self.points[0][1])), cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.color, 2)



class PolygonManager:
    def __init__(self):
        self.polygons = {}
        self.active_polygon = None

    def new_polygon(self, name, color):
        self.polygons[name] = Polygon(name, color)
        self.active_polygon = self.polygons[name]

    def add_point_to_active(self, point):
        if self.active_polygon:
            self.active_polygon.add_point(point)

    def close_active(self):
        if self.active_polygon:
            self.active_polygon.close()

    def draw_all(self, frame):
        for polygon in self.polygons.values():
            polygon.draw(frame)

    def move_all_polygons(self, dx, dy):
        for polygon in self.polygons.values():
            if polygon.is_closed:
                polygon.points = [(x + dx, y + dy) for x, y in polygon.points]
    
    def rotate_all_polygons(self, theta):
        centers = []
        for polygon in self.polygons.values():
            if polygon.is_closed and polygon.points:
                pts = np.array(polygon.points, dtype=np.float32)
                cx, cy = np.mean(pts, axis=0)
                centers.append((cx, cy))

        if not centers:
            return

        global_cx = np.mean([c[0] for c in centers])
        global_cy = np.mean([c[1] for c in centers])

        cos_theta = np.cos(theta)
        sin_theta = np.sin(theta)

        for polygon in self.polygons.values():
            if polygon.is_closed and polygon.points:
                new_points = []
                for x, y in polygon.points:
                    x_shifted = x - global_cx
                    y_shifted = y - global_cy

                    x_rot = x_shifted * cos_theta - y_shifted * sin_theta
                    y_rot = x_shifted * sin_theta + y_shifted * cos_theta

                    x_new = x_rot + global_cx
                    y_new = y_rot + global_cy
                    new_points.append((x_new, y_new))
            polygon.points = new_points



class PageThree(QWidget):
    def __init__(self, stack, main_window):
        super().__init__()
        self.stack = stack
        self.main_window = main_window
        self.setFixedSize(1400, 950)
        self.area_summary = None
        self.raw_data = None
        self.df_raw_data = None
        self.df_area_summary = None
        self.current_experiment_id = None
        self.current_experiment_name = None
        self.current_experiment_date = None
        self.total_time = "ไม่มีปรากฏข้อมูล"
        self.total_area = "ไม่มีปรากฏข้อมูล"
        self.experiment_time = "ไม่มีปรากฏข้อมูล"

        self.switch_page = QPushButton("กลับไปยังหน้าแรก")
        self.switch_page.clicked.connect(self.switch_to_home_page)
        self.switch_page.setObjectName("MainButton")

        self.csv_export = QPushButton("Export to CSV")
        self.csv_export.clicked.connect(self.export_to_csv)
        self.csv_export.setObjectName("YellowButton")

        self.excel_export = QPushButton("Export to Excel")
        self.excel_export.clicked.connect(self.export_to_excel)
        self.excel_export.setObjectName("YellowButton")

        self.theme_dropdown = QComboBox()
        self.theme_dropdown.setFixedSize(180, 32)
        self.theme_dropdown.setObjectName("ThemeDropdown")

        self.theme_dropdown.addItem("🌞 Light Theme", "light")
        self.theme_dropdown.addItem("🌜 Dark Theme", "dark")
        self.theme_dropdown.addItem("🌸 Pastel Theme", "pastel")
        self.theme_dropdown.addItem("🌈 Default Theme", "default")

        current_index = self.theme_dropdown.findData(self.main_window.get_theme())
        if current_index != -1:
            self.theme_dropdown.setCurrentIndex(current_index)

        self.theme_dropdown.currentIndexChanged.connect(self.change_theme)
        self.experiment_dropdown = self.create_experiment_dropdown()

        self.experiment_info = QLabel(f"Experiment ID: {self.current_experiment_id}\t\tExperiment Name: {self.current_experiment_name}\tExperiment Date: {self.current_experiment_date}")

        self.bar_graph = FigureCanvas(plt.Figure(figsize=(4.5, 3.5)))
        self.line_graph = FigureCanvas(plt.Figure(figsize=(4.5, 3.5)))
        self.pie_graph = FigureCanvas(plt.Figure(figsize=(4.5, 3.5)))

        self.main_layout = QVBoxLayout()

        top_row_layout = QHBoxLayout()
        top_row_layout.addWidget(self.experiment_info) 
        top_row_layout.addStretch()                  
        top_row_layout.addWidget(self.theme_dropdown)

        self.dropdown_layout = QVBoxLayout()
        self.dropdown_layout.addLayout(top_row_layout)
        self.dropdown_layout.addWidget(self.experiment_dropdown)

        self.card_frame = QFrame()
        self.card_frame.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.card_frame.setLineWidth(2)
        self.card_layout = QGridLayout()
        self.card_frame.setLayout(self.card_layout)

        self.total_time_label = QLabel(f"ระยะเวลาของพื้นที่ทั้งหมด:\n\n\n\n\t\t{self.total_time}")
        self.total_time_label.setAlignment(Qt.AlignTop)
        self.total_time_label.setStyleSheet("font-size: 16px;")
        self.total_area_label = QLabel(f"จำนวนพื้นที่ทั้งหมด:\n\n\n\n\t\t{self.total_area}")
        self.total_area_label.setAlignment(Qt.AlignTop)
        self.total_area_label.setStyleSheet("font-size: 16px;")
        self.experiment_time_label = QLabel(f"ระยะเวลาการทดลอง:\n\n\n\n\t\t{self.experiment_time}")
        self.experiment_time_label.setAlignment(Qt.AlignTop)
        self.experiment_time_label.setStyleSheet("font-size: 16px;")
        self.card_layout.addWidget(self.experiment_time_label, 0, 0)
        self.card_layout.addWidget(self.total_time_label, 0, 1)
        self.card_layout.addWidget(self.total_area_label, 1, 0)
        self.card_layout.setContentsMargins(20, 20, 20, 20)

        self.graph_layout = QGridLayout()
        self.graph_layout.addWidget(self.card_frame, 0, 0)
        self.graph_layout.addWidget(self.bar_graph, 0, 1)
        self.graph_layout.addWidget(self.line_graph, 1, 0)
        self.graph_layout.addWidget(self.pie_graph, 1, 1)
        self.graph_layout.setRowMinimumHeight(0, 350)
        self.graph_layout.setRowMinimumHeight(1, 350)
        self.graph_layout.setColumnMinimumWidth(0, 450)
        self.graph_layout.setColumnMinimumWidth(1, 450)
        self.main_layout.setStretchFactor(self.graph_layout, 1)   

        self.button_layout = QHBoxLayout()
        self.button_layout.addStretch()  
        self.button_layout.addWidget(self.csv_export)
        self.button_layout.addWidget(self.excel_export)
        self.button_layout.addWidget(self.switch_page)
        self.button_layout.addStretch()  

        self.main_layout.addLayout(self.dropdown_layout) 
        self.main_layout.addLayout(self.graph_layout)                
        self.main_layout.addLayout(self.button_layout)    

        self.setLayout(self.main_layout)

        self.refresh()
    
    def update_theme_dropdown(self):
        current_theme = self.main_window.get_theme()
        index = self.theme_dropdown.findData(current_theme)
        if index != -1:
            self.theme_dropdown.blockSignals(True)
            self.theme_dropdown.setCurrentIndex(index)
            self.theme_dropdown.blockSignals(False)
    
    def load_graph_theme(self, theme):
        plt.rcdefaults()
        if theme == "dark":
            sns.set_theme(style="darkgrid")
            plt.rcParams.update({
                "figure.facecolor": "#121212",
                "axes.facecolor": "#1e1e1e",
                "axes.edgecolor": "#0f7f4f",
                "grid.color": "#2a4f4f",
                "axes.labelcolor": "#0f7f4f",
                "xtick.color": "#0f7f4f",
                "ytick.color": "#0f7f4f",
                "text.color": "#0f7f4f",
                "axes.titlecolor": "#0f7f4f",
                "legend.facecolor": "#1e1e1e",
                "legend.edgecolor": "#0f7f4f",
        })

        elif theme == "light":
            sns.set_theme(style="whitegrid")
            plt.rcParams.update({
                "figure.facecolor": "#ddecf9",      
                "axes.facecolor": "#ffffff",        
                "axes.edgecolor": "#336699",        
                "grid.color": "#cce0ff",            
                "axes.labelcolor": "#003366",       
                "xtick.color": "#003366",           
                "ytick.color": "#003366",           
                "text.color": "#003366",            
                "axes.titlecolor": "#00264d",       
                "legend.facecolor": "#e6f2ff",      
                "legend.edgecolor": "#336699",      
        })

        elif theme == "pastel":
            sns.set_theme(style="whitegrid", palette="pastel")
            plt.rcParams.update({
                "figure.facecolor": "#fdedf5",      
                "axes.facecolor": "#faf6f8",        
                "axes.edgecolor": "#d6a5c9",        
                "grid.color": "#f2d9e6",            
                "axes.labelcolor": "#cc6699",       
                "xtick.color": "#cc6699",           
                "ytick.color": "#cc6699",           
                "text.color": "#b34780",            
                "axes.titlecolor": "#b34780",       
                "legend.facecolor": "#ffe6f0",      
                "legend.edgecolor": "#ffcce7",      
        })

        elif theme == "default":
            sns.set_theme(style="whitegrid")
            plt.rcParams.update({
                "figure.facecolor": "#e6e6e6",      
                "axes.facecolor": "#f2f2f2",        
                "axes.edgecolor": "#999999",        
                "grid.color": "#cccccc",            
                "axes.labelcolor": "#444444",       
                "xtick.color": "#444444",           
                "ytick.color": "#444444",          
                "text.color": "#333333",           
                "axes.titlecolor": "#444444",       
                "legend.facecolor": "#e0e0e0",      
                "legend.edgecolor": "#b3b3b3",      
        })

    def change_theme(self, index):
        theme = self.theme_dropdown.itemData(index)
        if theme:
            self.main_window.set_theme(theme)
            self.main_window.load_theme(theme)

            self.load_graph_theme(theme)

            self.update_graph()
    
    def sanitize_filename(self,filename):
        invalid_chars = r'[<>:"|?*]'
        sanitized = re.sub(invalid_chars, '_', filename)
        sanitized = sanitized.strip().strip('.')
        return sanitized
    
    def _write_csv(self, data, output_file, headers):
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
                for row in data:
                    writer.writerow(row)
        except OSError as e:
            print(f"Error writing to CSV file {output_file}: {e}")
            raise

    def _write_excel(self, data, worksheet, headers):
        if not isinstance(worksheet, Worksheet):
            raise TypeError(f"Expected Worksheet object, got {type(worksheet).__name__} instead")
        
        try:
            worksheet.append(headers)
            for row in data:
                worksheet.append(row)
        except Exception as e:
            print(f"Error writing to Excel worksheet {worksheet.title}: {e}")
            raise
    
    def export_to_csv(self):
        if not self.area_summary and not self.raw_data:
            print("Not found area summary and rawdata")
            return
        
        if self.area_summary :
            summary_file = os.path.join('export', f"{self.current_experiment_date}_{self.current_experiment_name}_area_summary.csv")
            summary_area_file = self.sanitize_filename(summary_file)
            summary_headers = ['area_id', 'experiment_id', 'area_name', 'color', 'hit_count', 'total_time', 'area_point']
            self._write_csv(self.area_summary, summary_area_file, summary_headers)
            print(f"Exported area_summary to {summary_file}")

        if self.raw_data:
            rawdata_file = os.path.join('export', f"{self.current_experiment_date}_{self.current_experiment_name}_raw_data.csv")
            rawdata_name_file = self.sanitize_filename(rawdata_file)
            rawdata_headers = ['experiment_id', 'area_id', 'timestamp', 'frame_count', 'area_name', 'rat_position_x', 'rat_position_y']
            self._write_csv(self.raw_data, rawdata_name_file, rawdata_headers)
            print(f"Exported raw_data to {rawdata_file}")

    def export_to_excel(self):
        if not self.area_summary and not self.raw_data:
            print("No data to export: both area_summary and raw_data are empty")
            return

        excel_file = os.path.join('export', f"{self.current_experiment_date}_{self.current_experiment_name}_data.xlsx")
        excel_file_sanitized = self.sanitize_filename(excel_file)
        output_dir = os.path.dirname(excel_file_sanitized)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        try:
            workbook = Workbook()
            default_sheet = workbook.active
            if self.area_summary or self.raw_data:
                workbook.remove(default_sheet)

            if self.area_summary:
                headers = ['area_id', 'experiment_id', 'area_name', 'color', 'hit_count', 'total_time', 'area_point']
                ws_summary = workbook.create_sheet(title="Area Summary")
                self._write_excel(self.area_summary, ws_summary, headers)

            if self.raw_data:
                headers = ['experiment_id', 'area_id', 'time_stamp', 'frame_count', 'area_name', 'rat_position_x', 'rat_position_y']
                ws_raw_data = workbook.create_sheet(title="Raw Data")
                self._write_excel(self.raw_data, ws_raw_data, headers)

            if workbook.sheetnames:
                workbook.save(excel_file_sanitized)
                print(f"Exported data to {excel_file_sanitized}")
            else:
                print("No sheets created; Excel file not saved")

        except Exception as e:
            print(f"Error writing to Excel file {excel_file_sanitized}: {e}")
            raise
    
    def create_experiment_dropdown(self):
        dropdown = QComboBox()
        all_experiments = self.main_window.db.get_all_experiments()
        dropdown.addItem("เลือกการทดลอง", 0)
        for experiment in all_experiments:
            dropdown.addItem(experiment[2], experiment[0])
        
        dropdown.setFixedHeight(40)
        dropdown.setFont(QFont("Arial", 20))
        dropdown.currentIndexChanged.connect(self.on_experiment_change)

        return dropdown

    def update_graph(self):
        print("Updating graphs...")

        self.bar_graph.figure.clear()
        self.line_graph.figure.clear()
        self.pie_graph.figure.clear()

        has_area_summary = self.df_area_summary is not None and not self.df_area_summary.empty
        has_raw_data = self.df_raw_data is not None and not self.df_raw_data.empty

        try:
            ax_line = self.line_graph.figure.add_subplot(111)
            if has_raw_data:
                sns.lineplot(data=self.df_raw_data, x="Timestamp", y="X", hue="Area Name", ax=ax_line)
                ax_line.set_title("x position per time")
                ax_line.set_xlabel("Time (seconds)")
                ax_line.set_ylabel("X position")
            else:
                ax_line.text(0.5, 0.5, "No data available\nOr invalid data", ha='center', va='center', fontsize=14)
                ax_line.set_axis_off()
            self.line_graph.figure.tight_layout()

            ax_bar = self.bar_graph.figure.add_subplot(111)
            ax_pie = self.pie_graph.figure.add_subplot(111)
            if has_area_summary:
                print("Generating bar and pie graphs")
                sns.barplot(data=self.df_area_summary, x="Area Name", y="Hit Count", hue="Area Name", palette=list(self.df_area_summary["Color"]), legend=False, ax=ax_bar, edgecolor='#444444', linewidth=1)
                for i, v in enumerate(self.df_area_summary["Hit Count"]):
                    ax_bar.text(i, (v/2), str(v), ha='center', va='bottom', fontsize=10)
                ax_bar.set_title("Area per number of detections")
                ax_bar.set_xlabel("Area Name")
                ax_bar.set_ylabel("Number of Detections")

                if self.df_area_summary["Total Time"].sum() > 0:
                    ax_pie.pie(self.df_area_summary["Total Time"], labels=self.df_area_summary["Area Name"], colors=self.df_area_summary["Color"], shadow=True, autopct='%1.1f%%')
                    ax_pie.set_title("Area per total time")
                else : 
                    print("No valid data available for pie graph")
                    ax_pie.text(0.5, 0.5, "No data available\nOr invalid data", ha='center', va='center', fontsize=14)
                    ax_pie.set_axis_off()
            else:
                print("No valid data available for bar and pie graphs")
                ax_bar.text(0.5, 0.5, "No data available\nOr invalid data", ha='center', va='center', fontsize=14)
                ax_pie.text(0.5, 0.5, "No data available\nOr invalid data", ha='center', va='center', fontsize=14)
                ax_bar.set_axis_off()
                ax_pie.set_axis_off()
            
            self.pie_graph.figure.tight_layout()
            self.bar_graph.figure.tight_layout()


        except Exception as e:
            print(f"Error generating graphs: {e}")
            ax_bar.text(0.5, 0.5, f"Error occurred: {str(e)}", ha='center', va='center', fontsize=14)
            ax_pie.text(0.5, 0.5, f"Error occurred: {str(e)}", ha='center', va='center', fontsize=14)
            ax_line.text(0.5, 0.5, f"Error occurred: {str(e)}", ha='center', va='center', fontsize=14)
            ax_bar.set_axis_off()
            ax_pie.set_axis_off()
            ax_line.set_axis_off()
            self.bar_graph.figure.tight_layout()
            self.pie_graph.figure.tight_layout()
            self.line_graph.figure.tight_layout()

        self.bar_graph.draw()
        self.line_graph.draw()
        self.pie_graph.draw()

    def prepare_data_for_graph(self):
        self.df_raw_data = None
        self.df_area_summary = None

        def parse_color(color_str):
            try:
                b, g, r = map(int, color_str.strip('()').split(','))
                return f'#{r:02x}{g:02x}{b:02x}'
            except:
                return color_str
            
        if self.raw_data:
            try:
                self.df_raw_data = pd.DataFrame(self.raw_data, columns=["Experiment ID", "Area ID", "Timestamp", "Frame Count", "Area Name", "X", "Y"])
                self.df_raw_data["Timestamp"] = pd.to_numeric(self.df_raw_data["Timestamp"], errors="coerce")
                self.df_raw_data["X"] = pd.to_numeric(self.df_raw_data["X"], errors="coerce")
                self.df_raw_data["Y"] = pd.to_numeric(self.df_raw_data["Y"], errors="coerce")
                self.df_raw_data["Area Name"] = self.df_raw_data["Area Name"].fillna("Unknown")
                print("Raw DataFrame:\n", self.df_raw_data.head())

                self.experiment_time = str(self.df_raw_data["Timestamp"].max()) + "  วินาที"
                self.experiment_time_label.setText(f"ระยะเวลาการทดลอง:\n\n\n\n\t\t{self.experiment_time}")
            except Exception as e:
                print(f"Error preparing raw_data: {e}")
                self.df_raw_data = None
                self.experiment_time = "ไม่มีปรากฏข้อมูล"
                self.experiment_time_label.setText(f"ระยะเวลาการทดลอง:\n\n\n\n\t\t{self.experiment_time}")

        if self.area_summary:
            try:
                self.df_area_summary = pd.DataFrame(self.area_summary, columns=["ID", "Experiment ID", "Area Name", "Color", "Hit Count", "Total Time", "Area Point"])
                self.df_area_summary["Hit Count"] = pd.to_numeric(self.df_area_summary["Hit Count"], errors="coerce")
                self.df_area_summary["Total Time"] = pd.to_numeric(self.df_area_summary["Total Time"], errors="coerce")
                self.df_area_summary["Color"] = self.df_area_summary["Color"].apply(parse_color)
                print("Area Summary DataFrame:\n", self.df_area_summary.head())

                self.total_time = str(self.df_area_summary["Total Time"].sum()) + "  วินาที"
                self.total_area = str(len(self.df_area_summary)) + "  พื้นที่"
                self.total_area_label.setText(f"จำนวนพื้นที่ทั้งหมด:\n\n\n\n\t\t{self.total_area}")
                self.total_time_label.setText(f"ระยะเวลาของพื้นที่ทั้งหมด:\n\n\n\n\t\t{self.total_time}")
            except Exception as e:
                print(f"Error preparing area_summary: {e}")
                self.df_area_summary = None
                self.total_area = "ไม่มีปรากฏข้อมูล"
                self.total_time = "ไม่มีปรากฏข้อมูล"
                self.total_area_label.setText(f"จำนวนพื้นที่ทั้งหมด:\n\n\n\n\t\t{self.total_area}")
                self.total_time_label.setText(f"ระยะเวลาของพื้นที่ทั้งหมด:\n\n\n\n\t\t{self.total_time}")
        
        self.update_graph()

    def refresh(self):
        self.experiment_dropdown.blockSignals(True)
        self.experiment_dropdown.clear()
        all_experiments = self.main_window.db.get_all_experiments()
        self.experiment_dropdown.addItem("เลือกการทดลอง", 0)
        for experiment in all_experiments:
            self.experiment_dropdown.addItem(experiment[2], experiment[0])
        self.experiment_dropdown.blockSignals(False)

        experiment_id = self.main_window.get_experiment_id()
        index = self.experiment_dropdown.findData(experiment_id) if experiment_id else 0
        self.experiment_dropdown.setCurrentIndex(index)
        self.on_experiment_change(index)
    
    def on_experiment_change(self, index):
        self.area_summary = None
        self.raw_data = None

        if index > 0:
            selected_id = self.experiment_dropdown.itemData(index)
            self.area_summary = self.main_window.db.get_area_summary_by_experiment_id(selected_id)
            self.raw_data = self.main_window.db.get_raw_data_by_experiment_id(selected_id)
            self.current_experiment_id = selected_id
            experiment = self.main_window.db.get_experiment_by_id(selected_id)
            self.current_experiment_name = experiment[2] if experiment else "None"
            self.current_experiment_date = experiment[3] if experiment else "None"
            self.experiment_info.setText(f"Experiment ID: {self.current_experiment_id}\t\tExperiment Name: {self.current_experiment_name}\tExperiment Date: {self.current_experiment_date}")

            if self.area_summary and self.raw_data:
                print(f"\nLoad Data success Experiment ID: {self.current_experiment_id} Experiment Name: {self.current_experiment_name}\narea_summary:\n{self.area_summary[0]}\nraw_data:\n{self.raw_data[0]}")
            elif self.area_summary or self.raw_data:
                print(f"\nLoad Data incomplete Experiment ID: {self.current_experiment_id} Experiment Name: {self.current_experiment_name}\narea_summary:\n{self.area_summary[0] if self.area_summary else None}\nraw_data:\n{self.raw_data[0] if self.raw_data else None}")
            else:
                print(f"\nLoad Data fail Experiment ID: {self.current_experiment_id} Experiment Name: {self.current_experiment_name}")
                print(f"Area summary data not found: {self.area_summary}")
                print(f"Raw data not found: {self.raw_data}")
        else:
            print("No experiment selected")
            self.clear_data()

        self.prepare_data_for_graph()
    
    def clear_data(self):
        self.area_summary = None
        self.raw_data = None
        self.df_raw_data = None
        self.df_area_summary = None
        self.current_experiment_id = None
        self.current_experiment_name = None
        self.current_experiment_date = None
        self.total_time = "ไม่มีปรากฏข้อมูล"
        self.total_area = "ไม่มีปรากฏข้อมูล"
        self.experiment_time = "ไม่มีปรากฏข้อมูล"
        self.experiment_time_label.setText(f"ระยะเวลาการทดลอง:\n\n\n\n\t\t{self.experiment_time}")
        self.total_area_label.setText(f"จำนวนพื้นที่ทั้งหมด:\n\n\n\n\t\t{self.total_area}")
        self.total_time_label.setText(f"ระยะเวลาของพื้นที่ทั้งหมด:\n\n\n\n\t\t{self.total_time}")
        self.experiment_info.setText(f"Experiment ID: {self.current_experiment_id}\t\tExperiment Name: {self.current_experiment_name}\tExperiment Date: {self.current_experiment_date}")
        
    def switch_to_home_page(self):
        self.experiment_dropdown.setCurrentIndex(self.experiment_dropdown.findData(0))
        self.main_window.set_experiment_id(None)
        self.clear_data()
        self.main_window.switch_to_page(0)
        

        
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_theme = "default"
        self.setWindowTitle("mice detection")
        self.setWindowIcon(QIcon("assets/mouse.png"))
        self.fps = 30

        self.stack = QStackedWidget()
        self.video_path = None
        self.experiment_id = None
        self.experiment_name = None

        self.db = DatabaseManager()

        self.page1 = PageOne(self.stack, self)
        self.page2 = PageTwo(self.stack, self)
        self.page3 = PageThree(self.stack, self)

        self.stack.addWidget(self.page1)
        self.stack.addWidget(self.page2)
        self.stack.addWidget(self.page3)

        self.setCentralWidget(self.stack)

        self.setFixedSize(self.page1.size()) 

        self.center_window()  

        self.load_theme(self.current_theme)

    def switch_to_page(self, index):
        self.stack.setCurrentIndex(index)
        current_widget = self.stack.currentWidget()
        self.setFixedSize(current_widget.size()) 
        self.center_window()  

        if index == 0 and isinstance(current_widget, PageOne):
            current_widget.update_theme_dropdown()

        if index == 1 and isinstance(current_widget, PageTwo):
            current_widget.update_video()

        if index == 2 and isinstance(current_widget, PageThree):  
            current_widget.refresh()
            current_widget.update_theme_dropdown()

    def center_window(self):
        window_rect = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        window_rect.moveCenter(center_point)
        self.move(window_rect.topLeft()) 

    def load_theme(self, theme_name):
        theme_files = {
            "light": "style/light.qss",
            "dark": "style/dark.qss",
            "default": "style/default.qss",
            "pastel": "style/pastel.qss"
        }
        if theme_name not in theme_files:
            print(f"Error: Theme '{theme_name}' not supported.")
            return
        try:
            with open(theme_files[theme_name], "r", encoding="utf-8") as style_file:
                app = QApplication.instance()
                app.setStyleSheet(style_file.read())
                self.current_theme = theme_name
        except FileNotFoundError:
            print(f"Error: QSS file '{theme_files[theme_name]}' not found.")
        except Exception as e:
            print(f"Error loading theme '{theme_name}': {e}")

    def set_video_path(self, video_path):
        self.video_path = video_path

    def get_video_path(self):
        return self.video_path
    
    def set_fps(self, fps):
        self.fps = fps

    def get_fps(self):
        return self.fps
    
    def set_experiment_name(self, experiment_name):
        self.experiment_name = experiment_name

    def get_experiment_name(self):
        return self.experiment_name
    
    def set_experiment_id(self, experiment_id):
        self.experiment_id = experiment_id

    def get_experiment_id(self):
        return self.experiment_id

    def set_theme(self, theme_name):
        self.current_theme = theme_name

    def get_theme(self):
        return self.current_theme

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()