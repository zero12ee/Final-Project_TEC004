import sys
sys.path.insert(0, 'd:\\Code\\Performance Tracker\\server')
import csv
import io

# Simulate what the API endpoint does
# Open the file the same way Flask would
with open('c:\\Users\\ASUS\\Downloads\\test 1.csv', 'rb') as f:
    csv_bytes = f.read()

# Create a file-like object
file_obj = io.BytesIO(csv_bytes)

# Read content to decode
content = file_obj.read()
print(f"Content type: {type(content)}")
print(f"First 100 bytes: {content[:100]}")

# Decode
if isinstance(content, bytes):
    for encoding in ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']:
        try:
            decoded = content.decode(encoding)
            print(f"Successfully decoded with {encoding}")
            break
        except:
            pass

# Process quotes
lines = decoded.split('\n')
processed_lines = []
for line in lines:
    if line.startswith('"') and line.endswith('"'):
        line = line[1:-1]
    processed_lines.append(line)
content_str = '\n'.join(processed_lines)

# Parse with dialect detection
file_obj = io.StringIO(content_str)
try:
    sample = '\n'.join(content_str.split('\n')[:5])
    print(f"\nSample for dialect detection:")
    print(repr(sample))
    dialect = csv.Sniffer().sniff(sample, delimiters=',;\t|')
    print(f"Detected dialect delimiter: {repr(dialect.delimiter)}")
except Exception as e:
    print(f"Dialect detection failed: {e}")
    dialect = 'excel'

# Read as CSV
file_obj = io.StringIO(content_str)
reader = csv.DictReader(file_obj, dialect=dialect)
rows = list(reader)

print(f"\nTotal rows: {len(rows)}")
if rows:
    print(f"Headers: {list(rows[0].keys())}")
    print(f"First row: {dict(rows[0])}")
