import sys
import json
sys.path.insert(0, 'server')
from database import Database  # type: ignore

db = Database()

# Get the most recent user's courses
db.cursor.execute('SELECT id FROM Users ORDER BY id DESC LIMIT 1')
user = db.cursor.fetchone()

if user:
    user_id = user['id']
    courses = db.get_courses_for_user(user_id)
    
    # Show Linear Algebra details
    for course in courses:
        if 'Linear Algebra' in course['name']:
            print('=== Linear Algebra Components ===')
            for comp in course['components']:
                print(f"  {comp['name']}: score={comp.get('score')}, keys={list(comp.keys())}")
