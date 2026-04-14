import pyodbc

conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=UFunUShareDB;UID=sa;PWD=Ushare!2025;charset=utf8')
cursor = conn.cursor()

# Use parameterized query
sql = "INSERT INTO classification_records (user_id, garbage_type, recognition_method, points_earned, dustbin_lng, dustbin_lat, dustbin_name) VALUES (?, ?, ?, ?, ?, ?, ?)"

# Use the exact Unicode values
params = (
    1,
    '可回收',  # 直接中文字符串
    'text',
    1,
    116.338829,
    39.949510,
    '22号楼南侧'
)

print(f"Params: {params}")
cursor.execute(sql, params)
conn.commit()

# Verify
cursor.execute("SELECT TOP 1 garbage_type, dustbin_name FROM classification_records ORDER BY id DESC")
row = cursor.fetchone()
if row:
    print(f"Inserted: garbage_type={row[0]!r}, dustbin_name={row[1]!r}")
else:
    print("No rows found")

conn.close()
