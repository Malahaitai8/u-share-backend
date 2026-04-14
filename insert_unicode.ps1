$ErrorActionPreference = 'SilentlyContinue'
$conn = New-Object System.Data.SqlClient.SqlConnection
$conn.ConnectionString = 'Server=localhost;Database=UFunUShareDB;User ID=sa;Password=Ushare!2025;'
$conn.Open()

# Insert using sp_executesql with proper Unicode
$sql = @"
SET NOCOUNT ON;
DELETE FROM classification_records;

INSERT INTO classification_records (user_id, garbage_type, recognition_method, points_earned, dustbin_lng, dustbin_lat, dustbin_name)
VALUES (1, N'可回收', 'text', 1, 116.338829, 39.949510, N'22号楼南侧');

INSERT INTO classification_records (user_id, garbage_type, recognition_method, points_earned, dustbin_lng, dustbin_lat, dustbin_name)
VALUES (1, N'厨余', 'text', 1, 116.340091, 39.949162, N'2号宿舍楼前');

SELECT garbage_type, dustbin_name FROM classification_records;
"@

$cmd = $conn.CreateCommand()
$cmd.CommandText = $sql
$reader = $cmd.ExecuteReader()
while ($reader.Read()) {
    Write-Host "garbage_type: $($reader.GetString(0)), dustbin_name: $($reader.GetString(1))"
}
$reader.Close()
$conn.Close()
