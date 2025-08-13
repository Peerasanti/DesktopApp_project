import sqlite3
import os
import datetime

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# DB_PATH = os.path.join(BASE_DIR, "database/data.db")

# conn = sqlite3.connect(DB_PATH)
# cursor = conn.cursor()

class DatabaseManager:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(self.base_dir, "database/data.db")
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

        self.initialize_database()

    def initialize_database(self):
        self.conn.execute('PRAGMA foreign_keys = ON')
        # experiment_type table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS experiment_type (
                experiment_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
                type_name TEXT
            )
        """)
        # experiments table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS experiments (
                experiment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_type_id INTEGER,
                name TEXT,
                date TIMESTAMP,
                detail_note TEXT,
                video_path TEXT,
                FOREIGN KEY (experiment_type_id) REFERENCES experiment_type(experiment_type_id)
            )
        """)
        # area_summary table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS area_summary (
                area_id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_id INTEGER,
                area_name TEXT,
                hit_count INTEGER,
                total_time REAL,
                area_point TEXT,
                FOREIGN KEY (experiment_id) REFERENCES experiments(experiment_id)
            )
        """)
        # raw_data table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS raw_data (
                experiment_id INTEGER,
                area_id INTEGER,
                time_stamp TIMESTAMP,
                frame_count INTEGER,
                area_name TEXT,
                rat_position_x INTEGER,
                rat_position_y INTEGER,
                FOREIGN KEY (experiment_id) REFERENCES experiments(experiment_id),
                FOREIGN KEY (area_id) REFERENCES area_summary(area_id)
            )
        """)
        self.conn.commit()

    def add_experiment_type(self, type_name):
        """เพิ่มประเภทการทดลอง"""
        try:
            self.cursor.execute("""
                INSERT INTO experiment_type (type_name)
                VALUES (?)
            """, (type_name,))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            self.conn.rollback()
            print(f"Error adding experiment type: {e}")
            return None

    def add_experiment(self, experiment_type_id, name, date, detail_note, video_path):
        """เพิ่มการทดลอง"""
        try:
            self.cursor.execute("""
                INSERT INTO experiments (experiment_type_id, name, date, detail_note, video_path)
                VALUES (?, ?, ?, ?, ?)
            """, (experiment_type_id, name, date, detail_note, video_path))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            self.conn.rollback()
            print(f"Error adding experiment: {e}")
            return None

    def save_area_summary(self, experiment_id, area_name, hit_count, total_time, area_point):
        """บันทึกข้อมูลสรุปของโซน"""
        try:
            self.cursor.execute("""
                INSERT INTO area_summary (experiment_id, area_name, hit_count, total_time, area_point)
                VALUES (?, ?, ?, ?, ?)
            """, (experiment_id, area_name, hit_count, total_time, area_point))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            self.conn.rollback()
            print(f"Error saving area summary: {e}")
            return None

    def save_raw_data(self, experiment_id, area_id, time_stamp, frame_count, area_name, rat_position_x, rat_position_y):
        """บันทึกข้อมูลดิบ"""
        try:
            self.cursor.execute("""
                INSERT INTO raw_data (experiment_id, area_id, time_stamp, frame_count, area_name, rat_position_x, rat_position_y)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (experiment_id, area_id, time_stamp, frame_count, area_name, rat_position_x, rat_position_y))
            self.conn.commit()
        except sqlite3.Error as e:
            self.conn.rollback()
            print(f"Error saving raw data: {e}")
        
    def close(self):
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None

    def __del__(self):
        self.close()

 