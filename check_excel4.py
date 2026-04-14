import zipfile
import xml.etree.ElementTree as ET

with zipfile.ZipFile('services/guide_service/data/dustbins.xlsx', 'r') as z:
    with z.open('xl/sharedStrings.xml') as f:
        content = f.read().decode('utf-8')
        print('First 2000 chars of shared strings:')
        print(content[:2000])
