# Base64 encoded Chinese strings to avoid write tool encoding issues
import pyodbc
import base64

conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=UFunUShareDB;UID=sa;PWD=Ushare!2025')
cursor = conn.cursor()

# Base64 strings for correct Chinese characters
type_recyclable = base64.b64decode('a2V5dGU=').decode('utf-8')  # this is 'key' not Chinese
# Let me use actual base64

# For '可回收' the UTF-8 bytes are: e5 9f 8b e5 8f a8
hex_recyclable = 'e59bb3e79c8be599a3'
type_recyclable = bytes.fromhex(hex_recyclable).decode('utf-8')

# For '22号楼南侧'
hex_name = '3232e58fb7e69d4e8a'
name_station = bytes.fromhex(hex_name).decode('utf-8')

print(f"Type: {type_recyclable!r}")
print(f"Name: {name_station!r}")

sql = "INSERT INTO classification_records (user_id, garbage_type, recognition_method, points_earned, dustbin_lng, dustbin_lat, dustbin_name) VALUES (?, ?, ?, ?, ?, ?, ?)"
cursor.execute(sql, (1, type_recyclable, 'text', 1, 116.338829, 39.949510, name_station))
conn.commit()

cursor.execute("SELECT TOP 1 garbage_type, dustbin_name FROM classification_records ORDER BY id DESC")
row = cursor.fetchone()
print(f"Result: garbage_type={row[0]!r}, dustbin_name={row[1]!r}")

conn.close()
