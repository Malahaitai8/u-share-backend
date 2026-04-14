import pyodbc
import subprocess

# Use sqlcmd directly to avoid Python encoding issues
sql = """
SET NOCOUNT ON;
DELETE FROM classification_records;

INSERT INTO classification_records (user_id, garbage_type, recognition_method, points_earned, dustbin_lng, dustbin_lat, dustbin_name)
VALUES (1, N'可回收', 'text', 1, 116.338829, 39.949510, N'22号楼南侧');

INSERT INTO classification_records (user_id, garbage_type, recognition_method, points_earned, dustbin_lng, dustbin_lat, dustbin_name)
VALUES (1, N'厨余', 'text', 1, 116.340091, 39.949162, N'2号宿舍楼前');

SELECT garbage_type, dustbin_name FROM classification_records;
"""

with open('insert_sql.sql', 'w', encoding='utf-8') as f:
    f.write(sql)

print("SQL file written")
