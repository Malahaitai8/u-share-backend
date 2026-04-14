import pyodbc
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=UFunUShareDB;UID=sa;PWD=Ushare!2025')
cursor = conn.cursor()

# 创建 location_stats 表
try:
    cursor.execute('''
    CREATE TABLE location_stats (
        id INT PRIMARY KEY IDENTITY,
        dustbin_name NVARCHAR(100),
        dustbin_lng FLOAT,
        dustbin_lat FLOAT,
        stat_date DATE NOT NULL,
        classification_count INT DEFAULT 0,
        created_at DATETIME DEFAULT GETDATE()
    )
    ''')
    print('Created location_stats table')
except Exception as e:
    print(f'location_stats: {e}')

conn.commit()

# 验证
cursor.execute('SELECT name FROM sys.columns WHERE object_id = OBJECT_ID(\'location_stats\') ORDER BY column_id')
columns = [row[0] for row in cursor.fetchall()]
print(f'\nlocation_stats columns ({len(columns)}):')
for col in columns:
    print(f'  - {col}')

conn.close()
