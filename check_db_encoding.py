import pyodbc
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=UFunUShareDB;UID=sa;PWD=Ushare!2025')
cursor = conn.cursor()

# Get the actual bytes from database
cursor.execute("SELECT TOP 1 garbage_type FROM classification_records WHERE garbage_type IS NOT NULL")
row = cursor.fetchone()
if row:
    val = row[0]
    print(f"Value repr: {val!r}")
    print(f"Value bytes: {val.encode('latin1')[:20].hex() if val else 'None'}")
    print(f"Value decode try: ", end="")
    try:
        print(val.encode('latin1').decode('utf-8'))
    except:
        print("FAILED")

# Check API response bytes
import requests
r = requests.get('http://localhost:8081/admin/stats/by-type?start_date=2026-03-01&end_date=2026-04-13')
import json
data = r.json()
print("\nAPI Response:")
print(json.dumps(data, ensure_ascii=False))

conn.close()
