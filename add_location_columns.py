import pyodbc
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=UFunUShareDB;UID=sa;PWD=Ushare!2025')
cursor = conn.cursor()

# 添加位置字段
try:
    cursor.execute('ALTER TABLE classification_records ADD dustbin_lng FLOAT NULL')
    print('Added dustbin_lng')
except Exception as e:
    print(f'dustbin_lng: {e}')

try:
    cursor.execute('ALTER TABLE classification_records ADD dustbin_lat FLOAT NULL')
    print('Added dustbin_lat')
except Exception as e:
    print(f'dustbin_lat: {e}')

try:
    cursor.execute('ALTER TABLE classification_records ADD dustbin_name NVARCHAR(100) NULL')
    print('Added dustbin_name')
except Exception as e:
    print(f'dustbin_name: {e}')

conn.commit()

# 验证表结构
cursor.execute('SELECT name FROM sys.columns WHERE object_id = OBJECT_ID(\'classification_records\') ORDER BY column_id')
columns = [row[0] for row in cursor.fetchall()]
print(f'\nclassification_records columns ({len(columns)}):')
for col in columns:
    print(f'  - {col}')

conn.close()
