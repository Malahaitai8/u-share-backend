import pyodbc
import base64

conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=UFunUShareDB;UID=sa;PWD=Ushare!2025')
cursor = conn.cursor()

# Get correct hex from Python's repr
type_recyclable = bytes.fromhex('e58fafe59b9ee694b6').decode('utf-8')
type_kitchen = bytes.fromhex('e5a4a9e4bda5').decode('utf-8')
type_harmful = bytes.fromhex('e69d8ee5a388').decode('utf-8')
type_other = bytes.fromhex('e585b6e4bb96').decode('utf-8')

name_station = bytes.fromhex('3232e58fb7e6a5bce58d97e4bea7').decode('utf-8')

print(f"Type recyclable: {type_recyclable!r}")
print(f"Type kitchen: {type_kitchen!r}")
print(f"Type harmful: {type_harmful!r}")
print(f"Type other: {type_other!r}")
print(f"Name station: {name_station!r}")

# Insert one record
sql = "INSERT INTO classification_records (user_id, garbage_type, recognition_method, points_earned, dustbin_lng, dustbin_lat, dustbin_name) VALUES (?, ?, ?, ?, ?, ?, ?)"
cursor.execute(sql, (1, type_recyclable, 'text', 1, 116.338829, 39.949510, name_station))
conn.commit()

cursor.execute("SELECT TOP 1 garbage_type, dustbin_name FROM classification_records ORDER BY id DESC")
row = cursor.fetchone()
print(f"Result: garbage_type={row[0]!r}, dustbin_name={row[1]!r}")

conn.close()
