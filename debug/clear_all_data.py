import sqlite3
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, "..", "database", "data.db")

if not os.path.exists(db_path):
    print(f"❌ Database not found at: {db_path}")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = cursor.fetchall()

    if not tables:
        print("⚠️ No user tables found in database.")
    else:
        for (table_name,) in tables:
            cursor.execute(f"DELETE FROM {table_name};")
            cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table_name}';")
            print(f"✅ Cleared table: {table_name}")

        conn.commit()
        print("🎉 All data has been cleared from the database.")

    conn.close()
