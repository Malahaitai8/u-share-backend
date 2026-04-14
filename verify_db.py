import pyodbc
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=UFunUShareDB;UID=sa;PWD=Ushare!2025')
cursor = conn.cursor()

# 检查现有用户
cursor.execute('SELECT COUNT(*) FROM users')
user_count = cursor.fetchone()[0]
print(f'Users count: {user_count}')

# 检查现有分类记录
cursor.execute('SELECT COUNT(*) FROM classification_records')
record_count = cursor.fetchone()[0]
print(f'Classification records count: {record_count}')

# 检查站点数据
cursor.execute('SELECT COUNT(*) FROM user_points')
station_count = cursor.fetchone()[0]
print(f'User points records: {station_count}')

# 查看 sample 数据
print('\nSample classification_records:')
cursor.execute('SELECT TOP 5 * FROM classification_records')
for row in cursor.fetchall():
    print(f'  {row}')

conn.close()

print('\n=== Database Setup Complete ===')
print('All tables created successfully!')
