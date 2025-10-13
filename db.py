import sqlite3
import os

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
                type_name TEXT UNIQUE
            )
        """)
        # add types of experiment in experiment_type table
        self.cursor.execute("""
            INSERT OR IGNORE INTO experiment_type (type_name) VALUES 
            ('Y-Maze'), 
            ('Novel Object Recognition Test'),
            ('Elevated Plus Maze'),
            ('Light/Dark Box Test: LDB'),
            ('Mirror Test')
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
                color TEXT,
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

    def save_area_summary(self, experiment_id, area_name, color, hit_count, total_time, area_point):
        """บันทึกข้อมูลสรุปของโซน"""
        try:
            self.cursor.execute("""
                INSERT INTO area_summary (experiment_id, area_name, color, hit_count, total_time, area_point)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (experiment_id, area_name, color, hit_count, total_time, area_point))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            self.conn.rollback()
            print(f"Error saving area summary: {e}")
            return None

    def save_raw_data_batch(self, data):
        """บันทึกข้อมูลดิบ"""
        try:
            self.cursor.executemany("""
                INSERT INTO raw_data (experiment_id, area_id, time_stamp, frame_count, area_name, rat_position_x, rat_position_y)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, data)
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            self.conn.rollback()
            print(f"Error saving raw data batch: {e}")
            return False

    def get_experiment_types(self):
        try:
            self.cursor.execute("SELECT * FROM experiment_type")
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching experiment types: {e}")
            return []
    
    def update_experiment(self, experiment_id, experiment_type_id, name, date, detail_note, video_path):
        try:
            self.cursor.execute("""
                UPDATE experiments 
                SET experiment_type_id = ?, name = ?, date = ?, detail_note = ?, video_path = ?
                WHERE experiment_id = ?
            """, (experiment_type_id, name, date, detail_note, video_path, experiment_id))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            self.conn.rollback()
            print(f"Error updating experiment: {e}")
            return False
        
    def update_experiment_name(self, experiment_id, new_name):
        try:
            self.cursor.execute("""
                UPDATE experiments 
                SET name = ?
                WHERE experiment_id = ?
            """, (new_name, experiment_id))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            self.conn.rollback()
            print(f"Error updating experiment name: {e}")
            return False
    
    def update_experiment_detail_note(self, experiment_id, new_detail_note):
        try:
            self.cursor.execute("""
                UPDATE experiments 
                SET detail_note = ?
                WHERE experiment_id = ?
            """, (new_detail_note, experiment_id))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            self.conn.rollback()
            print(f"Error updating experiment detail note: {e}")
            return False
    
    def update_area_summary(self, area_id, area_name, color, hit_count, total_time, area_point):
        try:
            self.cursor.execute("""
                UPDATE area_summary 
                SET area_name = ?, color = ?, hit_count = ?, total_time = ?, area_point = ?
                WHERE area_id = ?
            """, (area_name, color, hit_count, total_time, area_point, area_id))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            self.conn.rollback()
            print(f"Error updating area summary: {e}")
            return False
    
    def get_all_experiments(self):
        try:
            self.cursor.execute("SELECT * FROM experiments")
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching experiments: {e}")
            return []
        
    def get_all_area_summary(self):
        try:
            self.cursor.execute("SELECT * FROM area_summary")
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching area summary: {e}")
            return []
    
    def get_area_summary_by_experiment_id(self, experiment_id):
        try:
            self.cursor.execute("SELECT * FROM area_summary WHERE experiment_id = ?", (experiment_id,))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching area summary by experiment ID: {e}")
            return []
    
    def get_all_raw_data(self):
        try:
            self.cursor.execute("SELECT * FROM raw_data")
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching raw data: {e}")
            return []
    
    def get_raw_data_by_experiment_id(self, experiment_id):
        try:
            self.cursor.execute("SELECT * FROM raw_data WHERE experiment_id = ?", (experiment_id,))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching raw data by experiment ID: {e}")
            return []
        
    def get_experiment_name_by_id(self, experiment_id):
        try:
            self.cursor.execute("SELECT name FROM experiments WHERE experiment_id = ?", (experiment_id,))
            result = self.cursor.fetchone()
            return result[0] if result else None
        except sqlite3.Error as e:
            print(f"Error fetching experiment name by ID: {e}")
            return None
        
    def get_experiment_by_id(self, experiment_id):
        try:
            self.cursor.execute("SELECT * FROM experiments WHERE experiment_id = ?", (experiment_id,))
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Error fetching experiment by ID: {e}")
            return None
    
    def get_experiment_note_by_id(self, experiment_id):
        try:
            self.cursor.execute("SELECT detail_note FROM experiments WHERE experiment_id = ?", (experiment_id,))
            result = self.cursor.fetchone()
            return result[0] if result else None
        except sqlite3.Error as e:
            print(f"Error fetching experiment note by ID: {e}")
            return None
    
    def delete_experiment_by_id(self, experiment_id):
        try:
            self.cursor.execute("DELETE FROM experiments WHERE experiment_id = ?", (experiment_id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            self.conn.rollback()
            print(f"Error deleting experiment: {e}")
            return False
    
    def delete_area_summary_by_experiment_id(self, experiment_id):
        try:
            self.cursor.execute("DELETE FROM area_summary WHERE experiment_id = ?", (experiment_id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            self.conn.rollback()
            print(f"Error deleting area summary: {e}")
            return False
        
    def delete_area_summary_by_id(self, area_id):
        try:
            self.cursor.execute("DELETE FROM area_summary WHERE area_id = ?", (area_id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            self.conn.rollback()
            print(f"Error deleting area summary: {e}")
            return False
    
    def delete_raw_data_by_experiment_id(self, experiment_id):
        try:
            self.cursor.execute("DELETE FROM raw_data WHERE experiment_id = ?", (experiment_id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            self.conn.rollback()
            print(f"Error deleting raw data: {e}")
            return False
    
    def get_experiment_type_by_id(self, experiment_type_id):
        try:
            self.cursor.execute("SELECT type_name FROM experiment_type WHERE experiment_type_id = ?", (experiment_type_id,))
            result = self.cursor.fetchone()
            return result[0] if result else None
        except sqlite3.Error as e:
            print(f"Error fetching experiment type by ID: {e}")
            return None
        
    def close(self):
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None

    def __del__(self):
        self.close()

 