# Performance Tracker - Codebase Documentation

##  Overview

Performance Tracker is a full-stack web application for managing academic performance and tracking course grades. It allows students to:
- Create courses and components
- Upload CSV files with performance data
- Track weighted grades and calculate passing probabilities
- View course details with pre-filled scores from CSV imports

**Tech Stack:**
- **Frontend:** React with Vite (JavaScript)
- **Backend:** Flask (Python)
- **Database:** SQLite3
- **API Communication:** Axios (HTTP client)

---

##  Project Structure

```
Performance Tracker/
├── client/                 # React frontend (Vite)
│   ├── src/
│   │   ├── App.jsx        # Main application component
│   │   ├── App.css        # Global styles
│   │   ├── main.jsx       # React entry point
│   │   ├── index.css      # Base styles
│   │   ├── assets/        # Static images
│   │   └── components/    # React components
│   │       ├── Login.jsx          # Login/Sign-up page
│   │       ├── Dashboard.jsx      # Course list and CSV upload
│   │       ├── CourseDetail.jsx   # Course view with score input
│   │       └── CourseCreator.jsx  # Manual course creation
│   ├── package.json       # Dependencies
│   ├── vite.config.js    # Vite configuration
│   └── eslint.config.js  # Linting rules
│
├── server/                 # Flask backend (Python)
│   ├── api_server.py      # Flask API routes and endpoints
│   ├── database.py        # SQLite database operations
│   ├── data_manager.py    # CSV parsing and import logic
│   ├── models.py          # Data models (if needed)
│   └── main.py            # Server entry point
│
├── data/                   # Data directory
│   ├── backup_export.json # Exported course data
│   ├── class_1_grades.csv # Sample CSV data
│   └── historical_data.csv
│
├── tests/                  # Test files
│   ├── debug_scores.py
│   ├── test_api_upload.py
│   └── ... other tests
│
├── temp/                   # Temporary files
│   └── ... temporary test uploads
│
├── acadence.db            # SQLite database file
├── requirements.txt       # Python dependencies
└── CODEBASE_GUIDE.md      # This file
```

---

##  Backend Architecture

### Database Schema (SQLite)

```
Users
├── id (INTEGER PRIMARY KEY)
├── username (TEXT UNIQUE)
├── email (TEXT)
└── password_hash (TEXT)

Courses
├── id (INTEGER PRIMARY KEY)
├── user_id (FK → Users)
├── name (TEXT)
├── expected_total (REAL, default 100)
├── passing_threshold (REAL, default 60)
└── created_at (TIMESTAMP)

CourseComponents
├── id (INTEGER PRIMARY KEY)
├── course_id (FK → Courses)
├── name (TEXT)
├── weight (REAL)
├── max_points (REAL)
└── score (REAL, nullable)  # Pre-filled from CSV
```

### Key Backend Files

#### 1. **server/api_server.py** - REST API Endpoints

Main Flask application with routes:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/signup` | POST | User registration |
| `/api/auth` | POST | User login |
| `/api/courses` | GET | Fetch user's courses |
| `/api/courses` | POST | Create new course |
| `/api/courses/{id}` | PUT | Update course |
| `/api/import-subject-scores` | POST | Upload & parse CSV |

**Key Feature:** Returns courses with database-generated component IDs and pre-filled scores from CSV

#### 2. **server/database.py** - Database Operations

`Database` class handles all SQLite operations:

**User Management:**
- `create_user()` - Register new user with hashed password
- `validate_user()` - Authenticate login credentials
- `get_user_by_username()` / `get_user_by_id()` - User lookup

**Course Management:**
- `create_course()` - Create course with components
- `update_course()` - Modify existing course
- `get_courses_for_user()` - Fetch all user courses with components
- `get_course()` - Get single course with components

**Password Security:**
- Uses PBKDF2 with SHA256 hashing
- Random salt per password (16 bytes)
- Constant-time comparison to prevent timing attacks

#### 3. **server/data_manager.py** - CSV Parsing

`DataManager` class processes CSV files:

**Key Features:**
- **Multi-encoding Support:** UTF-8-BOM, UTF-8, Latin-1, CP1252
- **Flexible Column Matching:** Fuzzy matching with candidates list
- **Quote Handling:** Removes quote-wrapped lines with Windows CRLF support
- **Dialect Detection:** Auto-detects CSV format (delimiter, quoting)
- **Student ID Tracking:** Extracts and groups by student
- **Empty Value Handling:** Distinguishes between 0 and null scores

**CSV Format Expected:**
```
Student_ID,Course_Name,Component_Name,Weight_Percentage,Max_Points,Points_Earned
AUS15065,Linear Algebra,Attendance,10,10,10
AUS15065,Linear Algebra,Assignment,20,100,85
AUS15065,Linear Algebra,Midterm,30,100,78
AUS15065,Linear Algebra,Final,40,100,82
AUS15065,Advanced Computer Programming,Attendance,10,10,9
```

**Column Name Candidates (Fuzzy Matching):**
- Student ID: `student_id`, `student`, `id`, `user_id`, `learner_id`
- Course: `course_name`, `subject`, `course`, `class`
- Component: `component_name`, `component`, `assessment_type`
- Score: `points_earned`, `score`, `marks`, `grade`
- Max Points: `max_points`, `total_points`, `out_of`, `possible`

---

##  Frontend Architecture

### Component Hierarchy

```
App
├── Login
├── Dashboard
│   ├── CSV Upload Area
│   └── Course List (CourseItem)
├── CourseDetail
│   ├── Component Inputs
│   └── Grade Calculator
└── CourseCreator
```

### Key Frontend Files

#### 1. **client/src/App.jsx** - Main Application

Root component managing:
- **Authentication:** Sign in/sign up
- **View Navigation:** Dashboard, course detail, course editor
- **Course Management:** Fetch, create, update
- **CSV Upload:** File selection and processing

**State Management:**
```javascript
const [user, setUser]                                    // Current user
const [view, setView]                                   // Current page
const [courses, setCourses]                             // User's courses
const [selectedCourse, setSelectedCourse]               // Course being viewed
const [pendingUploadFile, setPendingUploadFile]         // CSV file to upload
const [uploadPerformanceExpected, setUploadPerformanceExpected]  // Target score
const [isUploadingFile, setIsUploadingFile]             // Upload progress
```

**Key Handlers:**
- `handleSignIn()` - POST to `/api/auth`
- `handleSignUp()` - POST to `/api/signup`
- `handleProcessCsvUpload()` - POST FormData to `/api/import-subject-scores`
- `handleSaveCourse()` - PUT/POST to `/api/courses`

#### 2. **client/src/components/CourseDetail.jsx** - Course Display & Input

Displays course with component scores and grade calculation:

**Features:**
- **CSV Pre-population:** Auto-fills scores from CSV if available
- **Real-time Calculation:** Updates totals as user types
- **Grade Suggestion:** Calculates required scores to meet threshold
- **Weighted Grades:** Computes grade based on component weights

**Calculation Formula:**
```
For each component:
  Normalized Score = (Input Score / Max Points) × Weight

Current Total = Sum of Normalized Scores

Passing = Current Total ≥ Passing Threshold
```

**Example:**
- Attendance: 10/10 × 10% = 10.00%
- Assignment: 85/100 × 20% = 17.00%
- Midterm: 78/100 × 30% = 23.40%
- Final: 82/100 × 40% = 32.80%
- **Total: 83.20%**

#### 3. **client/src/components/Dashboard.jsx** - Course List

Displays:
- List of user's courses with component counts
- CSV upload interface
- Options to view/edit each course

#### 4. **client/src/components/Login.jsx** - Authentication

Sign in and sign up forms for user authentication

#### 5. **client/src/components/CourseCreator.jsx** - Manual Course Creation

Form to manually create courses and components (without CSV)

---

##  Data Flow

### CSV Import Flow

```
User Selects CSV File
    ↓
Frontend: handleProcessCsvUpload()
    ↓
POST FormData to /api/import-subject-scores
    ↓
Backend: DataManager.import_subject_scores_from_file()
    ├─ Decode file (multi-encoding support)
    ├─ Remove quote wrapping
    ├─ Detect CSV dialect
    ├─ Find columns (fuzzy matching)
    └─ Group by subject/student
    ↓
Backend: Database.create_course() for each subject
    ├─ Insert Course record
    └─ Insert CourseComponents with scores
    ↓
API Response: {createdCourses, parsed}
    ├─ createdCourses: With database IDs and scores
    └─ parsed: Summary of parsed data
    ↓
Frontend: Update courses state
    ↓
User Sees Courses with Pre-filled Scores ✓
```

### Grade Calculation Flow

```
User Views Course
    ↓
CourseDetail Component Loads
    ↓
Initialize State with CSV scores (if available)
    ↓
User Enters Missing Scores
    ↓
onChange → handleInputChange()
    ↓
Calculate componentsWithScore (useMemo)
    ├─ Parse each input to number
    ├─ Normalize: (score / maxPoints) × weight
    └─ Update currentTotal
    ↓
Display Updated Grade Percentage ✓
    ↓
User Clicks Calculate
    ↓
handleCalculate()
    ├─ Find empty components
    ├─ Calculate needed points
    ├─ Suggest required scores
    └─ Show if passing
    ↓
Display Suggestions ✓
```

---

##  Security Features

### Password Security
- **PBKDF2-SHA256:** Industry-standard hashing
- **Random Salt:** 16 bytes per password
- **Timing Attack Prevention:** Constant-time comparison

### Input Validation
- **Column Fuzzy Matching:** Handles various CSV formats
- **Multi-Encoding:** Prevents encoding-related vulnerabilities
- **Type Safety:** Float parsing with defaults

### Data Isolation
- **User-Level Filtering:** Courses only accessible to owner
- **CORS Enabled:** Controlled cross-origin requests
- **SQL Parameterization:** Prevents SQL injection

---

##  Important Code Concepts

### CSV Encoding Detection (data_manager.py)
```python
encodings = ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']
for encoding in encodings:
    try:
        decoded = content.decode(encoding)
        break
    except UnicodeDecodeError:
        continue
```
Tries multiple encodings in priority order, handles BOM (Byte Order Mark)

### Quote-Wrapped Line Handling (data_manager.py)
```python
for line in lines:
    line = line.rstrip()  # Remove Windows \r before quote check
    if line.startswith('"') and line.endswith('"'):
        line = line[1:-1]  # Remove quotes
```
Properly handles Windows CRLF line endings in CSV

### Fuzzy Column Matching (data_manager.py)
```python
def _find_column_name(row, candidates):
    for key in row.keys():
        normalized = _normalize_key(key)  # lowercase, underscores
        if normalized in candidates:      # matches fuzzy list
            return key
    return None
```
Finds columns like "Student_ID", "Student Id", "student_id" → `student_id`

### Component Score Pre-population (CourseDetail.jsx)
```javascript
const [inputs, setInputs] = useState(() =>
  course.components.reduce((acc, comp) => {
    // Show CSV score if available, else empty
    const value = comp.score !== null && comp.score !== undefined 
      ? String(comp.score) 
      : '';
    return { ...acc, [comp.id]: value };
  }, {})
);
```
Initializes input fields with CSV scores, shows empty for null values (not 0)

---

##  Common Issues & Solutions

### Issue: All Components Show Same Score (e.g., "82")
**Cause:** Components missing database IDs
**Solution:** Ensure API returns created courses with `components[].id` from database
**File:** `server/api_server.py` line 253+

### Issue: Empty CSV Scores Show as "0"
**Cause:** `_parse_float()` defaulting empty string to 0.0
**Solution:** Change default to `None` for scores, distinguishing empty from 0
**File:** `server/data_manager.py` line 135

### Issue: UTF-8 Encoding Error ("Can't Decode Byte 0xFF")
**Cause:** CSV has BOM (Byte Order Mark)
**Solution:** Add `utf-8-sig` to encoding attempts
**File:** `server/data_manager.py` line 95

### Issue: Windows Line Endings Breaking Quote Detection
**Cause:** `\r` character before quote check
**Solution:** `rstrip()` before checking quotes
**File:** `server/data_manager.py` line 77

---

##  Running the Application

### Backend (Flask)
```bash
cd server
python main.py
# Server runs on http://localhost:5000
```

### Frontend (Vite)
```bash
cd client
npm install
npm run dev
# App runs on http://localhost:5174
```

### Database
SQLite automatically initializes on first run
- Location: `server/acadence.db`
- Schema: Auto-created in `database.py` `_initialize_tables()`

---

##  Development Notes

### Adding New CSV Columns
Edit `data_manager.py` in `import_subject_scores_from_file()`:
```python
score_key = self._find_column_name(row, [
    'score', 'marks', 'points', 'obtained', 'grade', 'points_earned',
    'YOUR_NEW_COLUMN_NAME'  # Add here
])
```

### Changing Calculation Formula
Edit `CourseDetail.jsx` in `componentsWithScore` useMemo or `handleCalculate()`

### Database Schema Changes
Edit `database.py` `_initialize_tables()` and ensure migration logic

---

##  Key Libraries & APIs

**Backend:**
- `Flask` - Web framework
- `sqlite3` - Database
- `csv` - CSV parsing
- `hashlib` - Password hashing

**Frontend:**
- `React` - UI framework
- `Vite` - Build tool
- `Axios` - HTTP client
- `CSS3` - Styling

---

##  Testing

Test files organized in `tests/` folder:
- `test_csv_parse.py` - CSV parsing tests
- `test_scores_stored.py` - Database tests
- `test_api_upload.py` - API endpoint tests

Run tests:
```bash
cd tests
python test_scores_stored.py
```

---

##  Support

For code questions, refer to:
1. **This file** - Architecture overview
2. **Code comments** - Detailed function documentation
3. **Conversation history** - Problem-solving examples
4. **Test files** - Usage examples

---

*Last Updated: June 23, 2026*
