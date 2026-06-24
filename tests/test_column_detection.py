import sys
sys.path.insert(0, 'd:\\Code\\Performance Tracker\\server')
from data_manager import DataManager  # type: ignore

# Test the column detection
sample_row = {
    'student_id': 'AUS15065',
    'course_name': 'Linear Algebra',
    'component_name': 'Attendance',
    'weight_percentage': '10',
    'max_points': '10',
    'points_earned': '10'
}

print("Sample row (normalized keys):")
print(sample_row)
print()

# Test _find_column_name
student_id_key = DataManager._find_column_name(sample_row, [
    'student_id', 'student', 'id', 'user_id', 'learner_id', 'enrollment_id'
])
print(f"student_id_key: {student_id_key}")

subject_key = DataManager._find_column_name(sample_row, [
    'subject', 'course', 'course_name', 'class', 'category', 'module', 'topic'
])
print(f"subject_key: {subject_key}")

component_key = DataManager._find_column_name(sample_row, [
    'component', 'component_name', 'assessment', 'assessment_type', 'task', 'item', 'activity', 'section'
])
print(f"component_key: {component_key}")

# Try to get values
print()
print("Values:")
print(f"student_id: {sample_row.get(student_id_key, 'Unknown')}")
print(f"subject: {sample_row.get(subject_key, 'General')}")
print(f"component: {sample_row.get(component_key, '')}")
