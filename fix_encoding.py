import pandas as pd
import zipfile
import xml.etree.ElementTree as ET

file_path = 'services/guide_service/data/dustbins.xlsx'

# Try reading with different encodings
print("=== Try 1: Default openpyxl ===")
df = pd.read_excel(file_path)
print("Columns:", list(df.columns))

print("\n=== Try 2: With encoding hint ===")
# Check if the issue is the shared strings XML encoding
with zipfile.ZipFile(file_path, 'r') as z:
    with z.open('xl/sharedStrings.xml') as f:
        content = f.read()
        print(f"XML encoding declared: {content[:100]}")

# Try reading with xlrd for xls files
print("\n=== Try 3: Force UTF-8 ===")
import io
df = pd.read_excel(file_path, engine='openpyxl')
# Try to re-encode the column names
for col in df.columns:
    try:
        new_col = col.encode('latin1').decode('utf-8')
        print(f"Col {col!r} -> {new_col!r}")
    except:
        print(f"Col {col!r} -> FAILED")

# Check raw bytes
print("\n=== Check raw column name bytes ===")
for col in df.columns:
    print(f"{col}: {col.encode('utf-8')[:20].hex()}")
