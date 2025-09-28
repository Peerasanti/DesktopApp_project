import sqlite3
import os
import pandas as pd

# กำหนดพาธไปยังไฟล์ data.db
base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, "..", "database", "data.db")
print(os.path.exists(db_path))
size = 10
allow_print = False

try:
    # เชื่อมต่อกับฐานข้อมูล
    print("กำลังเชื่อมต่อกับฐานข้อมูล...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    print("เชื่อมต่อกับฐานข้อมูลเรียบร้อย")

    # 1. ดึงข้อมูลจากตาราง experiment_type
    cursor.execute("SELECT * FROM experiment_type")
    experiment_types = cursor.fetchmany(size)
    if allow_print:
        print("\n\n======================================")
        print("===== ข้อมูลในตาราง experiment_type ====")
        print("======================================")
        for row in experiment_types:
            print(f"ID: {row[0]}, Type Name: {row[1]}")

    # 2. ดึงข้อมูลจากตาราง experiments
    cursor.execute("SELECT * FROM experiments")
    experiments = cursor.fetchmany(size)
    if allow_print:
        print("\n\n======================================")
        print("====== ข้อมูลในตาราง experiments =======")
        print("======================================")
        for row in experiments:
            print(f"ID: {row[0]}, Type ID: {row[1]}, Name: {row[2]}, Date: {row[3]}, Detail: {row[4]}, Video Path: {row[5]}")

    # 3. ดึงข้อมูลจากตาราง area_summary
    cursor.execute("SELECT * FROM area_summary")
    area_summaries = cursor.fetchmany(size)
    if allow_print:
        print("\n\n======================================")
        print("====== ข้อมูลในตาราง area_summary ======")
        print("======================================")
        for row in area_summaries:
            print(f"ID: {row[0]}, Experiment ID: {row[1]}, Area Name: {row[2]}, Color: {row[3]}, Hit Count: {row[4]}, Total Time: {row[5]}, Area Point: {row[6]}")

    # 4. ดึงข้อมูลจากตาราง raw_data
    cursor.execute("SELECT * FROM raw_data")
    raw_data = cursor.fetchmany(size)
    if allow_print:
        print("\n\n======================================")
        print("======== ข้อมูลในตาราง raw_data ========")
        print("======================================")
        for row in raw_data:
            print(f"Experiment ID: {row[0]}, Area ID: {row[1]}, Timestamp: {row[2]}, Frame Count: {row[3]}, Area Name: {row[4]}, X: {row[5]}, Y: {row[6]}")

    # df_raw_data = pd.DataFrame(raw_data, columns=["Experiment ID", "Area ID", "Timestamp", "Frame Count", "Area Name", "X", "Y"])
    
except sqlite3.Error as e:
    print(f"เกิดข้อผิดพลาด: {e}")

finally:
    # ปิดการเชื่อมต่อ
    if conn:
        conn.close()
        print("\nปิดการเชื่อมต่อกับฐานข้อมูลเรียบร้อย")