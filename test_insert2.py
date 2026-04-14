import pyodbc
import random
from datetime import datetime, timedelta
import pandas as pd

conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=UFunUShareDB;UID=sa;PWD=Ushare!2025;charset=utf8'
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# Test insertion with Chinese
test_sql = "INSERT INTO classification_records (user_id, garbage_type, recognition_method, points_earned, dustbin_lng, dustbin_lat, dustbin_name) VALUES (1, N'可回收', 'text', 1, 116.338829, 39.949510, N'22号楼南侧')"
print(f"Executing: {test_sql}")
cursor.execute(test_sql)
conn.commit()

cursor.execute("SELECT TOP 3 garbage_type, dustbin_name FROM classification_records ORDER BY id DESC")
rows = cursor.fetchall()
for row in rows:
    print(f"Result: garbage_type={row[0]!r}, dustbin_name={row[1]!r}")

conn.close()
