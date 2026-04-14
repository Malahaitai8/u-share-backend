import pandas as pd

print('=== Reading with engine specified ===')
try:
    df = pd.read_excel('services/guide_service/data/dustbins.xlsx', engine='openpyxl')
    print('Columns:', [repr(c) for c in df.columns])
    print('First row name:', repr(df.iloc[0, 2]))
except Exception as e:
    print(f'Error: {e}')

print('\n=== Reading with xlrd ===')
try:
    df = pd.read_excel('services/guide_service/data/dustbins.xlsx', engine='xlrd')
    print('Columns:', [repr(c) for c in df.columns])
except Exception as e:
    print(f'Error: {e}')

print('\n=== Check if file is valid Excel ===')
import os
file_size = os.path.getsize('services/guide_service/data/dustbins.xlsx')
print(f'File size: {file_size} bytes')

import zipfile
try:
    with zipfile.ZipFile('services/guide_service/data/dustbins.xlsx', 'r') as z:
        print('ZIP contents:', z.namelist()[:5])
except Exception as e:
    print(f'Error: {e}')
