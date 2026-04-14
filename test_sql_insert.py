import pyodbc

conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=UFunUShareDB;UID=sa;PWD=Ushare!2025')
cursor = conn.cursor()

# Delete all existing records with garbage
cursor.execute("DELETE FROM classification_records")
conn.commit()
print("Deleted all records")

# Insert using raw SQL with actual Unicode characters
# We'll insert by running SQL directly

# First check what charset the connection is using
cursor.execute("SELECT @@VERSION")
print(f"SQL Server version: {cursor.fetchone()[0][:50]}")

# Try inserting with N'...' prefix
sql = "INSERT INTO classification_records (user_id, garbage_type, recognition_method, points_earned, dustbin_lng, dustbin_lat, dustbin_name) VALUES (1, N'可回收', 'text', 1, 116.338829, 39.949510, N'22号楼南侧')"
print(f"Executing SQL: {sql}")

try:
    cursor.execute(sql)
    conn.commit()
    print("Insert succeeded")
except Exception as e:
    print(f"Insert failed: {e}")

conn.close()
