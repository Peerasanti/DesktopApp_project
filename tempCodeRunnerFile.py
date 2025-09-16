class PageThree(QWidget):
    def __init__(self, stack, main_window):
        super().__init__()
        self.stack = stack
        self.main_window = main_window
        self.setFixedSize(1400, 950)
        self.area_summary = None
        self.raw_data = None

        self.summary_bar = MplCanvas(self, width=5, height=4, dpi=100)
        self.summary_bar.axes.set_title("Bar Chart")

        self.line_chart = MplCanvas(self, width=5, height=4, dpi=100)
        self.line_chart.axes.set_title("Line Chart")

        self.pie_chart = MplCanvas(self, width=5, height=4, dpi=100)
        self.pie_chart.axes.set_title("Pie Chart")

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
        self.theme_dropdown.setFixedSize(140, 32)
        self.theme_dropdown.setObjectName("ThemeDropdown")

        self.theme_dropdown.addItem("🌞 Light Theme", "light")
        self.theme_dropdown.addItem("🌜 Dark Theme", "dark")
        self.theme_dropdown.addItem("🌸 Pastel Theme", "pastel")
        self.theme_dropdown.addItem("🌈 Default Theme", "default")

        current_index = self.theme_dropdown.findData(self.main_window.current_theme)
        if current_index != -1:
            self.theme_dropdown.setCurrentIndex(current_index)

        self.theme_dropdown.currentIndexChanged.connect(self.change_theme)

        self.experiment_dropdown = self.create_experiment_dropdown()

        top_layout = QHBoxLayout()
        top_layout.addWidget(self.experiment_dropdown, stretch=2)  
        top_layout.addWidget(self.csv_export, stretch=1)
        top_layout.addWidget(self.excel_export, stretch=1)

        grid_layout = QGridLayout()
        grid_layout.addWidget(self.summary_bar, 0, 0)   
        grid_layout.addWidget(self.line_chart, 0, 1)  
        grid_layout.addWidget(self.pie_chart, 1, 0, 1, 2)  

        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch(1)
        bottom_layout.addWidget(self.switch_page)
        bottom_layout.addStretch(1)

        self.layout = QVBoxLayout()
        self.layout.addLayout(top_layout)
        self.layout.addLayout(grid_layout, stretch=4)
        self.layout.addLayout(bottom_layout)
        self.setLayout(self.layout)

        self.setLayout(self.layout)

        self.refresh()
