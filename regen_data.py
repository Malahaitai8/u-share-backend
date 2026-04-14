import pyodbc
import random
from datetime import datetime, timedelta
import pandas as pd

conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=UFunUShareDB;UID=sa;PWD=Ushare!2025')
cursor = conn.cursor()

dustbins_df = pd.read_excel('services/guide_service/data/dustbins_with_types.xlsx')
stations = dustbins_df[['站点名称', '经度', '纬度']].dropna().to_dict('records')
for s in stations:
    s['站点名称'] = str(s['站点名称']).strip()

users = [1, 2, 3]
user_weights = [0.5, 0.3, 0.2]

garbage_types = ['\u53ef\u56de\u6536', '\u53a8\u4f59', '\u6709\u5bb3', '\u5176\u4ed6']
garbage_weights = [0.4, 0.25, 0.1, 0.25]

methods = ['text', 'voice', 'image']
method_weights = [0.6, 0.2, 0.2]

end_date = datetime.now()

def weighted_choice(choices, weights):
    return random.choices(choices, weights=weights, k=1)[0]

def generate_records(count=1000):
    records = []
    for _ in range(count):
        days_ago = random.randint(0, 30)
        hours_ago = random.randint(0, 23)
        minutes_ago = random.randint(0, 59)
        created_at = end_date - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
        
        user_id = weighted_choice(users, user_weights)
        garbage_type = weighted_choice(garbage_types, garbage_weights)
        recognition_method = weighted_choice(methods, method_weights)
        station = random.choice(stations)
        
        records.append({
            'user_id': user_id,
            'garbage_type': garbage_type,
            'recognition_method': recognition_method,
            'points_earned': 1,
            'created_at': created_at,
            'dustbin_lng': station['\u7ecf\u5ea6'],
            'dustbin_lat': station['\u7eac\u5ea6'],
            'dustbin_name': station['\u7ad9\u70b9\u540d\u79f0']
        })
    return records

print('Generating 1000 records...')
records = generate_records(1000)

insert_sql = '''INSERT INTO classification_records (user_id, garbage_type, recognition_method, points_earned, created_at, dustbin_lng, dustbin_lat, dustbin_name) VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''

for record in records:
    cursor.execute(insert_sql, 
        record['user_id'],
        record['garbage_type'],
        record['recognition_method'],
        record['points_earned'],
        record['created_at'],
        record['dustbin_lng'],
        record['dustbin_lat'],
        record['dustbin_name']
    )

conn.commit()
print(f'Inserted {len(records)} records')

cursor.execute('SELECT DISTINCT garbage_type FROM classification_records')
print('Garbage types in DB:')
for row in cursor.fetchall():
    print(f'  Type: {row[0]}')

cursor.execute('SELECT COUNT(*) FROM classification_records')
print(f'Total records: {cursor.fetchone()[0]}')

conn.close()
print('Done!')
