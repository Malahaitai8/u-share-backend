$conn = New-Object System.Data.SqlClient.SqlConnection
$conn.ConnectionString = 'Server=localhost;Database=UFunUShareDB;User ID=sa;Password=Ushare!2025;'
$conn.Open()
$cmd = $conn.CreateCommand()
$cmd.CommandText = 'SELECT TOP 5 garbage_type, COUNT(*) as cnt FROM classification_records GROUP BY garbage_type'
$reader = $cmd.ExecuteReader()
while ($reader.Read()) {
    $val = $reader.GetString(0)
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($val)
    Write-Host "Type: $val | Bytes: $([System.BitConverter]::ToString($bytes))"
}
$conn.Close()
