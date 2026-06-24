import sys
sys.path.insert(0, 'd:\\Code\\Performance Tracker\\server')
from data_manager import DataManager  # type: ignore

# Simulate what the Flask endpoint does
dm = DataManager()

# Open the file the same way Flask would
with open('c:\\Users\\ASUS\\Downloads\\test 1.csv', 'rb') as f:
    csv_bytes = f.read()

# Create a file-like object
import io
file_obj = io.BytesIO(csv_bytes)

# Call the method
try:
    result = dm.import_subject_scores_from_file(
        file_obj,
        expected_totals={},
        default_expected_total=100.0,
    )
    
    print(f"Parsed {len(result['subjects'])} subjects/courses:")
    for subject in result['subjects']:
        print(f"\n  Course: {subject['subject']}")
        print(f"  Student IDs: {subject.get('studentIds', [])}")
        print(f"  Components: {len(subject['components'])}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
