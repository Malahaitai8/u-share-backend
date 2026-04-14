import pyodbc
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=UFunUShareDB;UID=sa;PWD=Ushare!2025')
cursor = conn.cursor()
cursor.execute("SELECT garbage_type, COUNT(*) FROM classification_records GROUP BY garbage_type")
for row in cursor.fetchall():
    t = row[0]
    print(f'Type: {t!r}, Count: {row[1]}')
conn.close()
