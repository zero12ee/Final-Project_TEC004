import mimetypes
import os
import uuid
from urllib import request

csv_path = os.path.join('server', 'temp_test.csv')
with open(csv_path, 'w', encoding='utf-8') as f:
    f.write('subject,component,score,max_points,weight\nMath,midterm,80,100,50\nMath,final,90,100,50\n')

boundary = uuid.uuid4().hex
body = []

def add_field(name, value):
    body.append(f'--{boundary}')
    body.append(f'Content-Disposition: form-data; name="{name}"')
    body.append('')
    body.append(str(value))

add_field('user_id', '1')
add_field('defaultExpectedTotal', '85')

with open(csv_path, 'rb') as f:
    filename = os.path.basename(csv_path)
    body.append(f'--{boundary}')
    body.append(f'Content-Disposition: form-data; name="csv_file"; filename="{filename}"')
    body.append('Content-Type: text/csv')
    body.append('')
    body.append(f.read().decode('utf-8'))

body.append(f'--{boundary}--')
body.append('')
body_bytes = '\r\n'.join(body).encode('utf-8')

req = request.Request('http://127.0.0.1:5000/api/import-subject-scores', data=body_bytes)
req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
req.add_header('Content-Length', str(len(body_bytes)))

try:
    with request.urlopen(req) as resp:
        print('STATUS', resp.status)
        print(resp.read().decode('utf-8'))
except Exception as e:
    print('ERROR', e)
