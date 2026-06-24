import csv
import io

# Check the test 1.csv file
with open('c:\\Users\\ASUS\\Downloads\\test 1.csv', 'r', encoding='utf-8-sig') as f:
    content = f.read()
    
print("File content (first 500 chars):")
print(repr(content[:500]))
print()

# Process like the code does
lines = content.split('\n')
processed_lines = []
for line in lines:
    if line.startswith('"') and line.endswith('"'):
        line = line[1:-1]
    processed_lines.append(line)
processed_content = '\n'.join(processed_lines)

# Parse
f_obj = io.StringIO(processed_content)
try:
    sample = '\n'.join(processed_content.split('\n')[:5])
    dialect = csv.Sniffer().sniff(sample, delimiters=',;\t|')
except:
    dialect = 'excel'
    
reader = csv.DictReader(f_obj, dialect=dialect)
rows = list(reader)
print(f"Total rows: {len(rows)}")
if rows:
    print(f"Headers: {list(rows[0].keys())}")
    print(f"\nFirst 3 rows:")
    for i, row in enumerate(rows):
        if i >= 3:
            break
        print(f"  Row {i}: {dict(row)}")
