# -*- coding: utf-8 -*-
import pyodbc
import random
from datetime import datetime, timedelta

# Unicode escape sequences for Chinese characters
GARBAGE_TYPES = [
    (r'\u53ef\u56de\u6536', 'recyclable'),  # 可回收
    (r'\u53a8\u4f59', 'kitchen'),            # 厨余
    (r'\u6709\u5bb3', 'harmful'),             # 有害
    (r'\u5176\u4ed6', 'other')                # 其他
]

STATIONS = [
    (r'\u0032\u0032\u53f7\u697c\u5357\u4fa7', 116.338829, 39.949510),
    (r'\u0032\u53f7\u5bbf\u820d\u697c\u524d', 116.340091, 39.949162),
    (r'\u5357\u95e8\u5c0f\u6811\u6797\u897f\u5355\u4fa7', 116.340865, 39.949415),
]

conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=UFunUShareDB;UID=sa;PWD=Ushare!2025;charset=utf8')
cursor = conn.cursor()

# Test with Unicode escapes
test_type = GARBAGE_TYPES[0][0].encode('utf-8').decode('unicode_escape')
test_name = STATIONS[0][0].encode('utf-8').decode('unicode_escape')

sql = "INSERT INTO classification_records (user_id, garbage_type, recognition_method, points_earned, dustbin_lng, dustbin_lat, dustbin_name) VALUES (?, ?, ?, ?, ?, ?, ?)"
cursor.execute(sql, (1, test_type, 'text', 1, STATIONS[0][1], STATIONS[0][2], test_name))
conn.commit()

cursor.execute("SELECT TOP 1 garbage_type, dustbin_name FROM classification_records ORDER BY id DESC")
row = cursor.fetchone()
print(f"Test: garbage_type={row[0]!r}, dustbin_name={row[1]!r}")

conn.close()
