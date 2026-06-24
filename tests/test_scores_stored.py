import sys
sys.path.insert(0, 'd:\\Code\\Performance Tracker\\server')
from database import Database  # type: ignore
import sqlite3

# Create a test to verify scores are being stored
db = Database()

# Get a recent course (should be one of the imported ones)
db.cursor.execute("SELECT id, name FROM Courses ORDER BY id DESC LIMIT 1")
course = db.cursor.fetchone()

if course:
    course_id = course['id']
    print(f"Testing course: {dict(course)}")
    print()
    
    # Check the components with scores
    db.cursor.execute("SELECT id, name, weight, max_points, score FROM CourseComponents WHERE course_id = ?", (course_id,))
    components = [dict(row) for row in db.cursor.fetchall()]
    
    print(f"Components in database:")
    for comp in components:
        print(f"  - {comp['name']}: score={comp['score']}, max={comp['max_points']}, weight={comp['weight']}")
    
    print()
    
    # Test the get_courses_for_user method
    db.cursor.execute("SELECT user_id FROM Courses WHERE id = ?", (course_id,))
    user_id = db.cursor.fetchone()['user_id']
    
    courses = db.get_courses_for_user(user_id)
    print(f"\nCourses for user {user_id}:")
    for course in courses:
        print(f"  Course: {course['name']}")
        for comp in course['components']:
            print(f"    - {comp['name']}: score={comp.get('score')}, max={comp['maxPoints']}, weight={comp['weight']}")
else:
    print("No courses found in database")
