import pyodbc
import random
from datetime import datetime, timedelta
import pandas as pd

# Try with different connection string
conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=UFunUShareDB;UID=sa;PWD=Ushare!2025;charset=utf8'
try:
    conn = pyodbc.connect(conn_str)
    print("Connected with charset=utf8")
except:
    conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=UFunUShareDB;UID=sa;PWD=Ushare!2025'
    conn = pyodbc.connect(conn_str)
    print("Connected without charset")

cursor = conn.cursor()

# Test insertion with Chinese
test_sql = "INSERT INTO classification_records (user_id, garbage_type, recognition_method, points_earned, dustbin_lng, dustbin_lat, dustbin_name) VALUES (1, N'可回收', 'text', 1, 116.338829, 39.949510, N'22号楼南侧')"
cursor.execute(test_sql)
conn.commit()

cursor.execute("SELECT TOP 1 garbage_type, dustbin_name FROM classification_records WHERE garbage_type = N'可回收' ORDER BY id DESC")
row = cursor.fetchone()
print(f"Test insert result: garbage_type={row[0]!r}, dustbin_name={row[1]!r}")

# Delete test record
cursor.execute("DELETE FROM classification_records WHERE id = (SELECT MAX(id) FROM classification_records)")
conn.commit()

conn.close()
print("Done!")
