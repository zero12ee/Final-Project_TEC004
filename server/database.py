# ==========================================
# DATABASE MODULE - server/database.py
# ==========================================
# Purpose: SQLite database wrapper for user authentication and course management
# Provides CRUD operations for Users, Courses, and CourseComponents
# Key Features:
#   - User registration and authentication with password hashing
#   - Course creation and management
#   - Component scoring and storage
#   - Automatic database schema initialization

import os
import sqlite3
import hashlib
import hmac

class Database:
    """
    SQLite Database Manager
    
    Handles all database operations including:
    - User authentication (registration, login)
    - Course creation and management
    - Component scoring and storage
    - Automatic schema initialization and upgrades
    """
    
    def __init__(self, db_name=None):
        """
        Initialize database connection and create schema
        
        Args:
            db_name: Path to SQLite database file (default: acadence.db in server dir)
        """
        if db_name is None:
            db_name = os.path.join(os.path.dirname(__file__), 'acadence.db')
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Return rows as dict-like objects
        self.cursor = self.conn.cursor()
        self._initialize_tables()

    def _initialize_tables(self):
        """
        Create database tables if they don't exist
        Also handles schema upgrades for existing databases
        """
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
                score REAL,
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
        self.cursor.execute("PRAGMA table_info(CourseComponents)")
        component_columns = {row['name'] for row in self.cursor.fetchall()}
        if 'score' not in component_columns:
            self.cursor.execute('ALTER TABLE CourseComponents ADD COLUMN score REAL')
        self.conn.commit()

    def _hash_password(self, password: str) -> str:
        """
        Hash password using PBKDF2 with SHA256
        Uses a random salt to prevent rainbow table attacks
        """
        salt = os.urandom(16)
        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100_000)
        return salt.hex() + ':' + pwd_hash.hex()

    def _verify_password(self, stored_hash: str, password: str) -> bool:
        """
        Verify that a plain text password matches the stored hash
        Uses constant-time comparison to prevent timing attacks
        """
        salt, pwd_hash = stored_hash.split(':')
        new_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), bytes.fromhex(salt), 100_000).hex()
        return hmac.compare_digest(new_hash, pwd_hash)

    def create_user(self, username: str, email: str, password: str) -> int:
        """
        Create a new user in the database
        Password is automatically hashed before storage
        
        Args:
            username: Unique username for login
            email: User email address
            password: Plain text password (will be hashed)
            
        Returns:
            int: New user ID
            
        Raises:
            RuntimeError: If insertion fails
        """
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
        """
        Fetch user by username (for login)
        
        Args:
            username: Username to search for
            
        Returns:
            dict: User data {id, username, email, password_hash} or None if not found
        """
        self.cursor.execute(
            'SELECT id, username, email, password_hash FROM Users WHERE username = ?',
            (username,),
        )
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def get_user_by_id(self, user_id: int):
        """
        Fetch user by ID (for session management)
        
        Args:
            user_id: User ID to look up
            
        Returns:
            dict: User data {id, username, email} or None if not found
        """
        self.cursor.execute('SELECT id, username, email FROM Users WHERE id = ?', (user_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def validate_user(self, username: str, password: str):
        """
        Authenticate user credentials for login
        
        Args:
            username: Username to validate
            password: Password to verify
            
        Returns:
            dict: {id, username, email} if valid, None if invalid credentials
        """
        user = self.get_user_by_username(username)
        if not user:
            return None
        if self._verify_password(user['password_hash'], password):
            return {'id': user['id'], 'username': user['username'], 'email': user['email']}
        return None

    def create_course(self, user_id: int, name: str, components: list, expected_total: float = 100.0, passing_threshold: float = 60.0) -> int:
        """
        Create a new course with associated components
        
        Args:
            user_id: ID of course owner
            name: Course name (e.g., "Linear Algebra\n(Student ID: AUS15065)")
            components: List of component dicts with {name, weight, maxPoints, score}
            expected_total: Target score expectation (default 100)
            passing_threshold: Minimum score to pass (default 60)
            
        Returns:
            int: New course ID
            
        Raises:
            RuntimeError: If insertion fails
        """
        self.cursor.execute(
            'INSERT INTO Courses (user_id, name, expected_total, passing_threshold) VALUES (?, ?, ?, ?)',
            (user_id, name, expected_total, passing_threshold),
        )
        course_id = self.cursor.lastrowid
        if course_id is None:
            raise RuntimeError('Failed to insert course')
        course_id = int(course_id)
        # Insert all components for this course
        for comp in components:
            self.cursor.execute(
                'INSERT INTO CourseComponents (course_id, name, weight, max_points, score) VALUES (?, ?, ?, ?, ?)',
                (
                    course_id,
                    comp['name'],
                    comp['weight'],
                    comp['maxPoints'],
                    comp.get('score'),  # Can be None for empty scores
                ),
            )
        self.conn.commit()
        return course_id

    def update_course(self, course_id: int, user_id: int, name: str, components: list, expected_total: float = 100.0, passing_threshold: float = 60.0) -> bool:
        """
        Update an existing course and its components
        Deletes old components and creates new ones
        
        Args:
            course_id: ID of course to update
            user_id: ID of course owner (for validation)
            name: Updated course name
            components: Updated list of components
            expected_total: Updated expectation score
            passing_threshold: Updated passing threshold
            
        Returns:
            bool: True if successful, False if course not found or not owned by user
        """
        self.cursor.execute(
            'UPDATE Courses SET name = ?, expected_total = ?, passing_threshold = ? WHERE id = ? AND user_id = ?',
            (name, expected_total, passing_threshold, course_id, user_id),
        )
        if self.cursor.rowcount == 0:
            return False
        self.cursor.execute('DELETE FROM CourseComponents WHERE course_id = ?', (course_id,))
        for comp in components:
            self.cursor.execute(
                'INSERT INTO CourseComponents (course_id, name, weight, max_points, score) VALUES (?, ?, ?, ?, ?)',
                (
                    course_id,
                    comp['name'],
                    comp['weight'],
                    comp['maxPoints'],
                    comp.get('score'),
                ),
            )
        self.conn.commit()
        return True

    def get_courses_for_user(self, user_id: int) -> list:
        """
        Fetch all courses for a user with their components
        
        Args:
            user_id: ID of user to fetch courses for
            
        Returns:
            list: Courses with structure:
                  [
                    {
                      'id': int,
                      'name': str,
                      'expectedTotal': float,
                      'passingThreshold': float,
                      'components': [
                        {'id': int, 'name': str, 'weight': float, 'maxPoints': float, 'score': float}
                      ]
                    }
                  ]
        """
        self.cursor.execute('SELECT id, name FROM Courses WHERE user_id = ?', (user_id,))
        courses = [dict(row) for row in self.cursor.fetchall()]
        # Fetch components for each course
        for course in courses:
            self.cursor.execute(
                'SELECT id, name, weight, max_points, score FROM CourseComponents WHERE course_id = ?',
                (course['id'],),
            )
            course['components'] = [
                {
                    'id': row['id'],
                    'name': row['name'],
                    'weight': row['weight'],
                    'maxPoints': row['max_points'],
                    'score': row['score'],  # May be None for unfilled scores
                }
                for row in self.cursor.fetchall()
            ]
            course['expectedTotal'] = course.get('expected_total', 100.0)
            course['passingThreshold'] = course.get('passing_threshold', 60.0)
        return courses

    def get_course(self, course_id: int, user_id: int):
        """
        Fetch a single course with all components
        Only returns if the course is owned by the specified user
        
        Args:
            course_id: ID of course to fetch
            user_id: ID of user to verify ownership
            
        Returns:
            dict: Course with components, or None if not found or not owned
        """
        self.cursor.execute(
            'SELECT id, user_id, name FROM Courses WHERE id = ? AND user_id = ?',
            (course_id, user_id),
        )
        row = self.cursor.fetchone()
        if not row:
            return None
        course = dict(row)
        # Fetch all components for this course
        self.cursor.execute(
            'SELECT id, name, weight, max_points, score FROM CourseComponents WHERE course_id = ?',
            (course_id,),
        )
        course['components'] = [
            {
                'id': comp['id'],
                'name': comp['name'],
                'weight': comp['weight'],
                'maxPoints': comp['max_points'],
                'score': comp['score'],
            }
            for comp in self.cursor.fetchall()
        ]
        course['expectedTotal'] = course.get('expected_total', 100.0)
        course['passingThreshold'] = course.get('passing_threshold', 60.0)
        return course
