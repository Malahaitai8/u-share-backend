import requests

r = requests.post('http://localhost:8081/token', data={'username': 'cy', 'password': 'cy123456'})
token = r.json().get('access_token')
headers = {'Authorization': f'Bearer {token}'}

r = requests.get('http://localhost:8081/admin/stats/export?start_date=2026-03-01&end_date=2026-04-13', headers=headers)
print(f'Export API: {r.status_code}')
print(f'Content type: {r.headers.get("content-type")}')
print(f'Content preview:')
print(r.text[:500])
