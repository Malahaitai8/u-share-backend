import requests
r = requests.get('http://localhost:8085/dustbins')
print(f'Status: {r.status_code}')
import json
data = r.json()
print(f'First station: {data[0]}')
