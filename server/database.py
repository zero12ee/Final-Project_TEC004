# ==========================================
# Author: Pham Gia Bao (Student ID: AUS15065)
# Project ID: TEC004/05
# Description: SP3 - SQLite Database Management
# ==========================================

import sqlite3

class DatabaseManager:
    def __init__(self, db_name="acadence.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._initialize_tables()

    def _initialize_tables(self):
        self.cursor.executescript('''
            -- 1. Users
            CREATE TABLE IF NOT EXISTS Users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            );

            -- 2. Courses
            CREATE TABLE IF NOT EXISTS Courses (
                course_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                course_name TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES Users(id)
            );

            -- 3. Components (The 6+ dynamic parts)
            CREATE TABLE IF NOT EXISTS Components (
                comp_id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER,
                name TEXT NOT NULL,
                weight REAL NOT NULL, -- e.g., 10.0 for 10%
                max_points REAL NOT NULL,
                input_points REAL, -- This is where user input is stored
                FOREIGN KEY(course_id) REFERENCES Courses(course_id)
            );
        ''')
        self.conn.commit()

    def execute_complex_query_gpa(self):
        query = '''
            SELECT s.name, AVG(g.score) as gpa
            FROM Students s
            JOIN Enrollments e ON s.person_id = e.student_id
            JOIN Grades g ON e.enrollment_id = g.enrollment_id
            GROUP BY s.person_id
            ORDER BY gpa DESC;
        '''
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
class Database:
    def __init__(self, db_name="acadence.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._initialize_tables()

    def _initialize_tables(self):
        self.cursor.executescript('''
            CREATE TABLE IF NOT EXISTS Users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT);
            CREATE TABLE IF NOT EXISTS Courses (id INTEGER PRIMARY KEY, user_id INTEGER, name TEXT);
            CREATE TABLE IF NOT EXISTS Components (
                id INTEGER PRIMARY KEY, 
                course_id INTEGER, 
                name TEXT, 
                weight REAL, 
                max_points REAL, 
                input_points REAL
            );
        ''')
        self.conn.commit()

    def add_user(self, username, password):
        self.cursor.execute("INSERT INTO Users (username, password) VALUES (?, ?)", (username, password))
        self.conn.commit()