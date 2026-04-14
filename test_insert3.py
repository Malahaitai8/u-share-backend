import pyodbc

conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=UFunUShareDB;UID=sa;PWD=Ushare!2025;charset=utf8')
cursor = conn.cursor()

# Use Unicode escape sequences to avoid encoding issues
garbage_type = '\u53ef\u56de\u6536'  # 可回收
dustbin_name = '22\u53f7\u697c\u5357\u4fa7'  # 22号楼南侧

test_sql = f"INSERT INTO classification_records (user_id, garbage_type, recognition_method, points_earned, dustbin_lng, dustbin_lat, dustbin_name) VALUES (1, N'{garbage_type}', 'text', 1, 116.338829, 39.949510, N'{dustbin_name}')"
print(f"SQL: {test_sql}")

cursor.execute(test_sql)
conn.commit()

cursor.execute(f"SELECT TOP 1 garbage_type, dustbin_name FROM classification_records WHERE garbage_type = N'{garbage_type}' ORDER BY id DESC")
row = cursor.fetchone()
print(f"Result: garbage_type={row[0]!r}, dustbin_name={row[1]!r}")

conn.close()
