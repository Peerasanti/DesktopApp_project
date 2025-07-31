# # db.py
# import sqlite3
# import os
# import datetime

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# DB_PATH = os.path.join(BASE_DIR, "database/data.db")

# conn = sqlite3.connect(DB_PATH)
# cursor = conn.cursor()

# def initialize_database():
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS records (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             polygon_name TEXT,
#             timestamp TEXT,
#             duration REAL,
#             count INTEGER
#         )
#     ''')
#     conn.commit()

# def log_polygon_event(name, duration, count):
#     timestamp = datetime.datetime.now().isoformat()
#     cursor.execute('''
#         INSERT INTO records (polygon_name, timestamp, duration, count)
#         VALUES (?, ?, ?, ?)
#     ''', (name, timestamp, duration, count))
#     conn.commit()

# def get_summary_data():
#     cursor.execute('''
#         SELECT polygon_name, COUNT(*), SUM(duration)
#         FROM records
#         GROUP BY polygon_name
#     ''')
#     return cursor.fetchall()
