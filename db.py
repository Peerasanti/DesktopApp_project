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
        if os.path.basename(self.db_path) == "data.db":
            self.conn.execute("""   
                CREATE TABLE IF NOT EXISTS experiments (
                    experiment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    experiment_name TEXT,
                    experiment_date TEXT NOT NULL,
                    experiment_detail TEXT,
                    data_path TEXT NOT NULL
                )
            """)
        else:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS zone_summary_data (
                    zone_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    zone_name TEXT,
                    hit_count INTEGER,
                    total_time REAL,
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS time_series_data (
                    time_series_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    zone_id TEXT,
                    FOREIGN KEY (zone_id) REFERENCES zone_summary_data(zone_id)
                )
            """)

        self.conn.commit()
        
    def close(self):
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None

    def __del__(self):
        self.close()

 