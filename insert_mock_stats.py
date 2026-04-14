import pyodbc
import random
from datetime import datetime, timedelta
import pandas as pd

DB_SERVER = "localhost"
DB_NAME = "UFunUShareDB"
DB_USER = "sa"
DB_PASSWORD = "Ushare!2025"

garbage_types = ["recyclable", "kitchen", "hazardous", "other"]
garbage_weights = [0.4, 0.25, 0.1, 0.25]

recognition_methods = ["text", "voice", "image"]
method_weights = [0.6, 0.2, 0.2]

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

def load_stations():
    try:
        df = pd.read_excel('services/guide_service/data/dustbins_with_types.xlsx')
        stations = []
        for _, row in df.iterrows():
            stations.append({
                'name': str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else '',
                'lng': float(row.iloc[1]) if pd.notna(row.iloc[1]) else 0,
                'lat': float(row.iloc[2]) if pd.notna(row.iloc[2]) else 0
            })
        return [s for s in stations if s['name']]
    except Exception as e:
        print(f"Error loading stations: {e}")
        return [{'name': '_unknown', 'lng': 0, 'lat': 0}]

def weighted_choice(choices, weights):
    return random.choices(choices, weights=weights, k=1)[0]

def insert_mock_data():
    users = get_users()
    if not users:
        print("No users found in database")
        return

    stations = load_stations()
    print(f"Loaded {len(stations)} stations")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM classification_records")
    cursor.execute("DELETE FROM user_points")
    print("Cleared existing data")

    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    for user in users:
        user_id = user[0]
        username = user[1]

        total_records = 0
        total_points = 0

        current_date = start_date
        while current_date <= end_date:
            records_per_day = random.randint(2, 5)

            for _ in range(records_per_day):
                hours_ago = random.randint(7, 21)
                minutes_ago = random.randint(0, 59)

                created_at = current_date + timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59))
                if created_at > end_date:
                    created_at = end_date

                garbage_type = weighted_choice(garbage_types, garbage_weights)
                method = weighted_choice(recognition_methods, method_weights)
                points = 1

                station = random.choice(stations) if stations else {'name': '', 'lng': 0, 'lat': 0}

                cursor.execute("""
                    INSERT INTO classification_records (user_id, garbage_type, recognition_method, points_earned, created_at, dustbin_lng, dustbin_lat, dustbin_name)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (user_id, garbage_type, method, points, created_at.strftime('%Y-%m-%d %H:%M:%S'), station['lng'], station['lat'], station['name']))

                total_records += 1
                total_points += points

            current_date += timedelta(days=1)

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