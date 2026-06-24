import csv
import io

with open('c:\\Users\\ASUS\\Downloads\\Example.csv', 'r', encoding='utf-8-sig') as f:
    content_str = f.read()
    
# Handle edge case: entire lines wrapped in quotes
lines = content_str.split('\n')
processed_lines = []
for line in lines:
    if line.startswith('"') and line.endswith('"'):
        line = line[1:-1]
    processed_lines.append(line)
content_str = '\n'.join(processed_lines)

print('Processed first 3 lines:')
for i, line in enumerate(content_str.split('\n')[:3]):
    print(f'  {i}: {repr(line)}')
print()

# Parse
f_obj = io.StringIO(content_str)
try:
    sample = '\n'.join(content_str.split('\n')[:5])
    dialect = csv.Sniffer().sniff(sample)
except:
    dialect = 'excel'
    
reader = csv.DictReader(f_obj, dialect=dialect)
rows = list(reader)
print(f'Total rows: {len(rows)}')
if rows:
    print('Headers:', list(rows[0].keys()))
    print('First row:', dict(rows[0]))
    if len(rows) > 3:
        print('4th row:', dict(rows[3]))
    
    # Group by course
    courses = {}
    for row in rows:
        course = row.get('Course_Name', 'Unknown')
        if course not in courses:
            courses[course] = []
        courses[course].append(row)
    
    print(f'\nFound {len(courses)} courses:')
    for course_name, course_rows in courses.items():
        print(f'  - {course_name}: {len(course_rows)} records')
