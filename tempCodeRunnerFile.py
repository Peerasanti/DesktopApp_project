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
        # self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setObjectName("VideoDisplay")
        self.video_label.setFixedSize(1000, 650)
        self.video_label.mousePressEvent = self.polygon_draw

        self.start_draw_button = QPushButton("✏️ เริ่มการวาดพื้นที่")
        self.start_draw_button.clicked.connect(self.start_drawing)

        self.stop_botton = QPushButton("⏸️ หยุดวิดีโอ / ▶️เริ่มวิดีโอ")
        self.stop_botton.clicked.connect(self.on_label_click)

        self.back_button = QPushButton("⬅️ ย้อนกลับ")
        self.back_button.clicked.connect(self.on_back_button_clicked)

        self.create_polygon_table()

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_draw_button)
        button_layout.addWidget(self.stop_botton)
        button_layout.addStretch()
        button_layout.addWidget(self.back_button)

        left_layout = QVBoxLayout()
        left_layout.addWidget(self.video_label)
        left_layout.addLayout(button_layout)

        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("🧩 รายการ Polygon"))
        right_layout.addWidget(self.polygon_table)
        right_layout.addStretch()

        main_layout = QHBoxLayout()
        main_layout.addLayout(left_layout, stretch=1)
        main_layout.addLayout(right_layout, stretch=1)
        self.setLayout(main_layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.next_frame)
