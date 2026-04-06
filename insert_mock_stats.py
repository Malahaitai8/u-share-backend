import pyodbc
import random
from datetime import datetime, timedelta

DB_SERVER = "localhost"
DB_NAME = "UFunUShareDB"
DB_USER = "sa"
DB_PASSWORD = "Ushare!2025"

garbage_types = ["可回收", "厨余", "有害", "其他"]
recognition_methods = ["text", "voice", "image"]

def get_connection():
    return pyodbc.connect(
        f'DRIVER={{ODBC Driver 17 for SQL Server}};'
        f'SERVER={DB_SERVER};'
        f'DATABASE={DB_NAME};'
        f'UID={DB_USER};'
        f'PWD={DB_PASSWORD}'
    )

def get_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM users")
    users = cursor.fetchall()
    conn.close()
    return users

def insert_mock_data():
    users = get_users()
    if not users:
        print("No users found in database")
        return

    conn = get_connection()
    cursor = conn.cursor()

    for user in users:
        user_id = user[0]
        username = user[1]

        total_records = random.randint(10, 50)
        total_points = 0

        for i in range(total_records):
            days_ago = random.randint(0, 60)
            hours_ago = random.randint(0, 23)
            minutes_ago = random.randint(0, 59)

            created_at = datetime.now() - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
            created_at_str = created_at.strftime('%Y-%m-%d %H:%M:%S')

            garbage_type = random.choice(garbage_types)
            method = random.choice(recognition_methods)
            points = 1

            cursor.execute("""
                INSERT INTO classification_records (user_id, garbage_type, recognition_method, points_earned, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, garbage_type, method, points, created_at_str))

            total_points += points

        cursor.execute("""
            INSERT INTO user_points (user_id, current_points, total_points, updated_at)
            VALUES (?, ?, ?, GETDATE())
        """, (user_id, total_points, total_points))

        print(f"User '{username}' (ID: {user_id}): {total_records} records, {total_points} points")

    conn.commit()
    conn.close()
    print(f"\nMock data inserted for {len(users)} users!")

if __name__ == "__main__":
    insert_mock_data()
