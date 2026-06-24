import requests
from pathlib import Path

path = Path('server/temp_test.csv')
path.write_text('subject,component,score,max_points,weight\nMath,midterm,80,100,50\nMath,final,90,100,50\n', encoding='utf-8')

files = {'csv_file': open(path, 'rb')}
data = {'user_id': '1', 'defaultExpectedTotal': '85'}
resp = requests.post('http://127.0.0.1:5000/api/import-subject-scores', files=files, data=data)
print('STATUS', resp.status_code)
print(resp.text)
