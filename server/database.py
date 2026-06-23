# server/database.py
import os
import sqlite3
import hashlib
import hmac

class Database:
    def __init__(self, db_name=None):
        if db_name is None:
            db_name = os.path.join(os.path.dirname(__file__), 'acadence.db')
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self._initialize_tables()

    def _initialize_tables(self):
        self.cursor.executescript('''
            CREATE TABLE IF NOT EXISTS Users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                email TEXT,
                password_hash TEXT
            );

            CREATE TABLE IF NOT EXISTS Courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                name TEXT,
                expected_total REAL DEFAULT 100,
                passing_threshold REAL DEFAULT 60,
                FOREIGN KEY(user_id) REFERENCES Users(id)
            );

            CREATE TABLE IF NOT EXISTS CourseComponents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER,
                name TEXT,
                weight REAL,
                max_points REAL,
                FOREIGN KEY(course_id) REFERENCES Courses(id)
            );
        ''')
        self.conn.commit()

        # Ensure existing databases are upgraded with the new columns.
        self.cursor.execute("PRAGMA table_info(Courses)")
        existing_columns = {row['name'] for row in self.cursor.fetchall()}
        if 'expected_total' not in existing_columns:
            self.cursor.execute('ALTER TABLE Courses ADD COLUMN expected_total REAL DEFAULT 100')
        if 'passing_threshold' not in existing_columns:
            self.cursor.execute('ALTER TABLE Courses ADD COLUMN passing_threshold REAL DEFAULT 60')
        self.conn.commit()

    def _hash_password(self, password: str) -> str:
        salt = os.urandom(16)
        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100_000)
        return salt.hex() + ':' + pwd_hash.hex()

    def _verify_password(self, stored_hash: str, password: str) -> bool:
        salt, pwd_hash = stored_hash.split(':')
        new_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), bytes.fromhex(salt), 100_000).hex()
        return hmac.compare_digest(new_hash, pwd_hash)

    def create_user(self, username: str, email: str, password: str) -> int:
        password_hash = self._hash_password(password)
        self.cursor.execute(
            'INSERT INTO Users (username, email, password_hash) VALUES (?, ?, ?)',
            (username, email, password_hash),
        )
        self.conn.commit()
        user_id = self.cursor.lastrowid
        if user_id is None:
            raise RuntimeError('Failed to insert user')
        return int(user_id)

    def get_user_by_username(self, username: str):
        self.cursor.execute(
            'SELECT id, username, email, password_hash FROM Users WHERE username = ?',
            (username,),
        )
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def get_user_by_id(self, user_id: int):
        self.cursor.execute('SELECT id, username, email FROM Users WHERE id = ?', (user_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def validate_user(self, username: str, password: str):
        user = self.get_user_by_username(username)
        if not user:
            return None
        if self._verify_password(user['password_hash'], password):
            return {'id': user['id'], 'username': user['username'], 'email': user['email']}
        return None

    def create_course(self, user_id: int, name: str, components: list, expected_total: float = 100.0, passing_threshold: float = 60.0) -> int:
        self.cursor.execute(
            'INSERT INTO Courses (user_id, name, expected_total, passing_threshold) VALUES (?, ?, ?, ?)',
            (user_id, name, expected_total, passing_threshold),
        )
        course_id = self.cursor.lastrowid
        # sqlite3.Cursor.lastrowid can be None in some typings; ensure an int is returned
        if course_id is None:
            raise RuntimeError('Failed to insert course')
        course_id = int(course_id)
        for comp in components:
            self.cursor.execute(
                'INSERT INTO CourseComponents (course_id, name, weight, max_points) VALUES (?, ?, ?, ?)',
                (course_id, comp['name'], comp['weight'], comp['maxPoints']),
            )
        self.conn.commit()
        return course_id

    def update_course(self, course_id: int, user_id: int, name: str, components: list, expected_total: float = 100.0, passing_threshold: float = 60.0) -> bool:
        self.cursor.execute(
            'UPDATE Courses SET name = ?, expected_total = ?, passing_threshold = ? WHERE id = ? AND user_id = ?',
            (name, expected_total, passing_threshold, course_id, user_id),
        )
        if self.cursor.rowcount == 0:
            return False
        self.cursor.execute('DELETE FROM CourseComponents WHERE course_id = ?', (course_id,))
        for comp in components:
            self.cursor.execute(
                'INSERT INTO CourseComponents (course_id, name, weight, max_points) VALUES (?, ?, ?, ?)',
                (course_id, comp['name'], comp['weight'], comp['maxPoints']),
            )
        self.conn.commit()
        return True

    def get_courses_for_user(self, user_id: int) -> list:
        self.cursor.execute('SELECT id, name FROM Courses WHERE user_id = ?', (user_id,))
        courses = [dict(row) for row in self.cursor.fetchall()]
        for course in courses:
            self.cursor.execute(
                'SELECT id, name, weight, max_points FROM CourseComponents WHERE course_id = ?',
                (course['id'],),
            )
            course['components'] = [
                {
                    'id': row['id'],
                    'name': row['name'],
                    'weight': row['weight'],
                    'maxPoints': row['max_points'],
                }
                for row in self.cursor.fetchall()
            ]
            course['expectedTotal'] = course.get('expected_total', 100.0)
            course['passingThreshold'] = course.get('passing_threshold', 60.0)
        return courses

    def get_course(self, course_id: int, user_id: int):
        self.cursor.execute(
            'SELECT id, user_id, name FROM Courses WHERE id = ? AND user_id = ?',
            (course_id, user_id),
        )
        row = self.cursor.fetchone()
        if not row:
            return None
        course = dict(row)
        self.cursor.execute(
            'SELECT id, name, weight, max_points FROM CourseComponents WHERE course_id = ?',
            (course_id,),
        )
        course['components'] = [
            {
                'id': comp['id'],
                'name': comp['name'],
                'weight': comp['weight'],
                'maxPoints': comp['max_points'],
            }
            for comp in self.cursor.fetchall()
        ]
        course['expectedTotal'] = course.get('expected_total', 100.0)
        course['passingThreshold'] = course.get('passing_threshold', 60.0)
        return course
