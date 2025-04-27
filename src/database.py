import sqlite3
from datetime import datetime

DB_Name = "Hydration_tracker.db"

def create_tables():
    conn = sqlite3.connect(DB_Name)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS water_intake (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            intake_ml INTEGER,
            date TEXT
        )
    """)
    conn.commit()
    conn.close()

def log_intake(user_id, intake_ml):
    conn = sqlite3.connect(DB_Name)
    cursor = conn.cursor()
    date_today = datetime.now().strftime('%d-%m-%y %H:%M:%S')
    cursor.execute(
        "INSERT INTO water_intake (user_id, intake_ml, date) VALUES (?, ?, ?)",
        (user_id, intake_ml, date_today)
    )
    conn.commit()
    conn.close()

def get_intake_history(user_id):
    conn = sqlite3.connect(DB_Name)
    cursor = conn.cursor()
    cursor.execute("SELECT intake_ml, date FROM water_intake WHERE user_id = ?", (user_id,))
    records = cursor.fetchall()
    conn.close()
    return records

def delete_user_history(user_id):
    conn = sqlite3.connect(DB_Name)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM water_intake WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_tables()
