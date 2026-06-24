import sys
sys.path.insert(0, 'd:\\Code\\Performance Tracker\\server')

from data_manager import DataManager  # type: ignore

dm = DataManager()

with open('c:\\Users\\ASUS\\Downloads\\Example.csv', 'r', encoding='utf-8-sig') as f:
    result = dm.import_subject_scores_from_file(f, default_expected_total=100)

print(f"Parsed {len(result['subjects'])} subjects/courses:")
for subject in result['subjects']:
    print(f"\n  Course: {subject['subject']}")
    print(f"  Student IDs: {subject.get('studentIds', [])}")
    print(f"  Components: {len(subject['components'])}")
    for comp in subject['components']:
        print(f"    - {comp['name']}: {comp['score']}/{comp['maxPoints']} (weight: {comp['weight']}%)")
