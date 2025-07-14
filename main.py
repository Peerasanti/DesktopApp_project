# Full path for run script: "C:\Users\WINDOWS\miniconda3\envs\rat_lab\python.exe" -u "d:\DesktopApp_project\main.py"

import sys
import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "1"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import tensorflow as tf
import cv2
import numpy as np
from PyQt5.QtWidgets import ( QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, 
                             QStackedWidget, QPushButton, QFileDialog, QDialog, QHBoxLayout, 
                             QFormLayout, QLineEdit, QDialogButtonBox, QDesktopWidget, QInputDialog,
                             QColorDialog, QTableWidget, QTableWidgetItem, QMessageBox)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QIcon, QPixmap, QImage, QFont, QColor

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
        if self.video_path:
            print(self.video_path)
            self.main_window.set_video_path(self.video_path)
            self.main_window.switch_to_page(1)
            self.timer.stop()
            self.is_playing = False
            self.status_label.setText("⏸️ วิดีโอถูกหยุด")
        else:
            self.label.setText("❌ ยังไม่ได้เลือกไฟล์วิดีโอหรือกล้อง")
            return

    def clear_data(self):
        if self.cap:
            self.cap.release()
        self.timer.stop()
        self.label.setText("🎥 เลือกไฟล์วิดีโอหรือกล้อง")
        self.status_label.setText("⏳ รอการเลือกวิดีโอหรือกล้อง")
        self.video_path = None
        self.cap = None
        self.is_playing = False



class PageTwo(QWidget):
    def __init__(self, stack, main_window):
        super().__init__()  
        self.stack = stack
        self.main_window = main_window
        self.is_playing = False
        self.cap = None
        self.model = tf.keras.models.load_model("model/model_for_rat_V2.keras", safe_mode=False)
        self.last_frame = None
        self.frame_count = 0
        self.process_every_n = 4

        self.polygon_manager = PolygonManager()
        self.drawing_polygon = False
        self.active_started = False
        self.mouse_pos = None
        self.polygon_name = ""
        self.polygon_color = (0, 255, 0)

        self.setFixedSize(1600, 900)  

        self.video_label = QLabel("📹 เริ่มการตรวจตำแหน่ง")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setObjectName("VideoDisplay")
        self.video_label.setFixedSize(1000, 650)
        self.video_label.mousePressEvent = self.polygon_draw

        self.start_draw_button = QPushButton("✏️ เริ่มการวาดพื้นที่")
        self.start_draw_button.clicked.connect(self.start_drawing)

        self.stop_botton = QPushButton("⏸️ หยุดวิดีโอ / ▶️เริ่มวิดีโอ")
        self.stop_botton.clicked.connect(self.on_label_click)

        self.back_button = QPushButton("⬅️ ย้อนกลับ")
        self.back_button.clicked.connect(self.on_back_button_clicked)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_draw_button)
        button_layout.addWidget(self.stop_botton)
        button_layout.addStretch()
        button_layout.addWidget(self.back_button)

        self.create_polygon_table()

        polygon_label = QLabel("🧾 รายการ Polygon")
        polygon_label.setAlignment(Qt.AlignCenter)
        polygon_label.setStyleSheet("font-size: 14px; color: #00ff99;")

        right_layout = QVBoxLayout()
        right_layout.addWidget(polygon_label)
        right_layout.addWidget(self.polygon_table)
        right_layout.addStretch()

        left_layout = QVBoxLayout()
        left_layout.addWidget(self.video_label)
        left_layout.addLayout(button_layout)

        main_layout = QHBoxLayout()
        main_layout.addLayout(left_layout, stretch=1)
        main_layout.addLayout(right_layout, stretch=1)
        self.setLayout(main_layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.next_frame)

    def delete_polygon(self, name):
        if name in self.polygon_manager.polygons:
            del self.polygon_manager.polygons[name]
            self.update_polygon_table()
            self.next_frame()
    
    def edit_polygon(self, name):
        pass
        # polygon = self.polygon_manager.polygons[name]
        # color = QColorDialog.getColor(QColor(*polygon.color))
        # if color.isValid():
        #     polygon.color = (color.blue(), color.green(), color.red())
        #     self.update_polygon_table()
        #     self.next_frame()
    
    def update_polygon_table(self):
        polygons = self.polygon_manager.polygons
        self.polygon_table.setRowCount(len(polygons))

        for i, (name, polygon) in enumerate(polygons.items()):
            name_item = QTableWidgetItem(name)
            color_item = QTableWidgetItem()
            color = polygon.color
            rgb_color = (color[2], color[1], color[0])
            qcolor = QColor(*rgb_color)
            color_item.setBackground(qcolor)
            color_item.setText(f"({rgb_color[0]}, {rgb_color[1]}, {rgb_color[2]})")

            btn_delete = QPushButton("ลบ")
            btn_delete.clicked.connect(lambda _, name=name: self.delete_polygon(name))

            btn_edit = QPushButton("แก้ไข")
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
            self.polygon_table.setCellWidget(i, 2, cell_widget)

    def create_polygon_table(self):
        self.polygon_table = QTableWidget()
        self.polygon_table.setColumnCount(3)
        self.polygon_table.setHorizontalHeaderLabels(["ชื่อ", "สี", "การจัดการ"])
        self.polygon_table.setFixedHeight(200)
        self.polygon_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.polygon_table.horizontalHeader().setStretchLastSection(True)

        font = self.polygon_table.font()
        font.setPointSize(10)
        self.polygon_table.setFont(font)
        self.polygon_table.verticalHeader().setDefaultSectionSize(36)

        self.update_polygon_table()

    def stop_video(self):
        self.timer.stop()  
        if self.cap:
            self.cap.release()  
            self.cap = None
        self.is_playing = False
    
    def on_back_button_clicked(self):
        self.stop_video()
        self.main_window.switch_to_page(0)

    def update_video(self):
        self.video_path = self.main_window.get_video_path()
        if self.video_path:
            if self.cap:
                self.cap.release()
            self.cap = cv2.VideoCapture(self.video_path)
            if self.cap.isOpened():
                self.is_playing = True
                self.timer.start(30)
            else:
                print("Error: ไม่สามารถเปิดวิดีโอจาก Path นี้ได้")
                self.cap = None
        else:
            print("Warning: video_path is None")

    def on_label_click(self, event):
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

        frame_display = cv2.resize(current_frame, (self.video_label.width(), self.video_label.height()), interpolation=cv2.INTER_CUBIC)

        input_frame = cv2.resize(current_frame, (128, 128), interpolation=cv2.INTER_CUBIC)
        input_frame = np.expand_dims(input_frame, axis=0)
        result = self.model.predict(input_frame)[0]  
        result = (result * 255).astype(np.uint8)

        mask = cv2.resize(result, (self.video_label.width(), self.video_label.height()), interpolation=cv2.INTER_CUBIC)

        _, binary_mask = cv2.threshold(mask, 100, 255, cv2.THRESH_BINARY)

        green_layer = np.zeros((mask.shape[0], mask.shape[1], 3), dtype=np.uint8)
        green_layer[:, :] = (0, 255, 0)

        green_masked = cv2.bitwise_and(green_layer, green_layer, mask=binary_mask)

        frame_display = frame_display.astype(np.uint8)
        overlay_frame = cv2.addWeighted(frame_display, 0.9, green_masked, 0.5, 0)

        self.polygon_manager.draw_all(overlay_frame)

        overlay_frame = cv2.cvtColor(overlay_frame, cv2.COLOR_BGR2RGB)
        h, w, ch = overlay_frame.shape
        qimg = QImage(overlay_frame.data, w, h, ch * w, QImage.Format_RGB888)
        margin = 10
        size = self.video_label.size()
        scaled_size = QSize(size.width() - margin * 2, size.height() - margin * 2)
        pixmap = QPixmap.fromImage(qimg).scaled(
            scaled_size, Qt.IgnoreAspectRatio, Qt.SmoothTransformation
        )
        self.video_label.setPixmap(pixmap)

    def start_drawing(self):
        name, ok = QInputDialog.getText(self, "ชื่อ Polygon", "กรุณาตั้งชื่อ")
        if not ok or not name.strip():
            name = f"Polygon-{len(self.polygon_manager.polygons) + 1}"

        color = QColorDialog.getColor()
        if not color.isValid():
            color = QColor(0, 255, 0)
        
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
            self.update_polygon_table()
            self.next_frame()
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



class Polygon:
    def __init__(self, name, color):
        self.points = []
        self.color = color
        self.name = name
        self.is_closed = False
    
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
            cv2.circle(frame, (x, y), 3, (255, 0, 0), -1)
        if self.points:
            cv2.putText(frame, self.name, self.points[0], cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.color, 2)



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



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("mice detection")
        self.setWindowIcon(QIcon("assets/mouse.png"))

        self.stack = QStackedWidget()
        self.video_path = None

        self.page1 = PageOne(self.stack, self)
        self.page2 = PageTwo(self.stack, self)

        self.stack.addWidget(self.page1)
        self.stack.addWidget(self.page2)

        self.setCentralWidget(self.stack)

        self.setFixedSize(self.page1.size()) 

        self.center_window()  

    def switch_to_page(self, index):
        self.stack.setCurrentIndex(index)
        current_widget = self.stack.currentWidget()
        self.setFixedSize(current_widget.size()) 
        self.center_window()  

        if index == 1 and isinstance(current_widget, PageTwo):
            current_widget.update_video()

    def center_window(self):
        window_rect = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        window_rect.moveCenter(center_point)
        self.move(window_rect.topLeft()) 

    def set_video_path(self, video_path):
        self.video_path = video_path

    def get_video_path(self):
        return self.video_path



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