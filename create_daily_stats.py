import pyodbc
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=UFunUShareDB;UID=sa;PWD=Ushare!2025')
cursor = conn.cursor()

# 创建 daily_stats 表
try:
    cursor.execute('''
    CREATE TABLE daily_stats (
        id INT PRIMARY KEY IDENTITY,
        stat_date DATE NOT NULL,
        total_classifications INT DEFAULT 0,
        total_points INT DEFAULT 0,
        recyclable_count INT DEFAULT 0,
        kitchen_count INT DEFAULT 0,
        harmful_count INT DEFAULT 0,
        other_count INT DEFAULT 0,
        voice_count INT DEFAULT 0,
        text_count INT DEFAULT 0,
        image_count INT DEFAULT 0,
        unique_users INT DEFAULT 0,
        created_at DATETIME DEFAULT GETDATE(),
        updated_at DATETIME DEFAULT GETDATE()
    )
    ''')
    print('Created daily_stats table')
except Exception as e:
    print(f'daily_stats: {e}')

conn.commit()

# 验证
cursor.execute('SELECT name FROM sys.columns WHERE object_id = OBJECT_ID(\'daily_stats\') ORDER BY column_id')
columns = [row[0] for row in cursor.fetchall()]
print(f'\ndaily_stats columns ({len(columns)}):')
for col in columns:
    print(f'  - {col}')

conn.close()
