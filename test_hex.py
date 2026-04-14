import pyodbc
import binascii

conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=UFunUShareDB;UID=sa;PWD=Ushare!2025;charset=utf8')
cursor = conn.cursor()

# Use hex to bypass encoding issues
hex_type = 'e59bb3e79c8be599a3'  # 可回收 in hex
hex_name = '3232e58fb7e69d4e8a'  # 22e58fb7e69d4e8a in hex

# Decode from hex to get correct string
correct_type = bytes.fromhex(hex_type).decode('utf-8')
correct_name = bytes.fromhex(hex_name).decode('utf-8')

print(f"Correct type: {correct_type!r}")
print(f"Correct name: {correct_name!r}")

sql = "INSERT INTO classification_records (user_id, garbage_type, recognition_method, points_earned, dustbin_lng, dustbin_lat, dustbin_name) VALUES (?, ?, ?, ?, ?, ?, ?)"
cursor.execute(sql, (1, correct_type, 'text', 1, 116.338829, 39.949510, correct_name))
conn.commit()

cursor.execute("SELECT TOP 1 garbage_type, dustbin_name FROM classification_records ORDER BY id DESC")
row = cursor.fetchone()
print(f"Inserted: garbage_type={row[0]!r}, dustbin_name={row[1]!r}")

conn.close()
