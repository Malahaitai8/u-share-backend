import requests
import json

r = requests.post('http://localhost:8081/token', data={'username': 'cy', 'password': 'cy123456'})
token = r.json().get('access_token')
headers = {'Authorization': f'Bearer {token}'}

# 测试趋势接口
r = requests.get('http://localhost:8081/admin/stats/trend?start_date=2026-03-01&end_date=2026-04-13&period=day', headers=headers)
print(f'/stats/trend: {r.status_code}')
if r.status_code == 200:
    data = r.json()
    trend = data.get("trend", [])
    print(f'Trend data: {len(trend)} records')
    for item in trend[:3]:
        print(f'  {item}')

# 测试按类型统计
r = requests.get('http://localhost:8081/admin/stats/by-type?start_date=2026-03-01&end_date=2026-04-13', headers=headers)
print(f'\n/stats/by-type: {r.status_code}')
if r.status_code == 200:
    print(json.dumps(r.json(), indent=2, ensure_ascii=False))

# 测试按识别方式统计
r = requests.get('http://localhost:8081/admin/stats/by-method?start_date=2026-03-01&end_date=2026-04-13', headers=headers)
print(f'\n/stats/by-method: {r.status_code}')
if r.status_code == 200:
    print(json.dumps(r.json(), indent=2, ensure_ascii=False))

# 测试按投放点统计
r = requests.get('http://localhost:8081/admin/stats/by-location?start_date=2026-03-01&end_date=2026-04-13', headers=headers)
print(f'\n/stats/by-location: {r.status_code}')
if r.status_code == 200:
    data = r.json()
    print(f'Location data: {len(data.get("stats", []))} stations')

# 测试排行榜
r = requests.get('http://localhost:8081/admin/stats/leaderboard?limit=5', headers=headers)
print(f'\n/stats/leaderboard: {r.status_code}')
if r.status_code == 200:
    print(json.dumps(r.json(), indent=2, ensure_ascii=False))

print('\n=== All API tests passed! ===')
