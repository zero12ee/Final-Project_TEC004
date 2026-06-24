# Code Documentation - Quick Reference

## 📚 All Documented Files

This document summarizes which files have been documented with detailed code comments and explains what each file does.

---

## ✅ Fully Documented Files

### Backend Files (Python)

#### 1. **server/database.py** ✓
**Status:** Fully documented with comprehensive docstrings
**Purpose:** SQLite database wrapper for user authentication and course management

**Documented Methods:**
- `__init__()` - Initialize database connection
- `_initialize_tables()` - Create schema and handle upgrades
- `_hash_password()` - Secure password hashing with salt
- `_verify_password()` - Verify login credentials
- `create_user()` - Register new user
- `get_user_by_username()` - Look up user for login
- `get_user_by_id()` - Fetch user by ID
- `validate_user()` - Authenticate credentials
- `create_course()` - Create course with components
- `update_course()` - Modify existing course
- `get_courses_for_user()` - Fetch all user courses
- `get_course()` - Get single course with components

**Key Learning Points:**
- PBKDF2-SHA256 password hashing
- SQLite schema creation and upgrades
- Relationship management (Users → Courses → Components)
- Query optimization with proper column selection

---

#### 2. **server/data_manager.py** ✓
**Status:** Fully documented with comprehensive docstrings
**Purpose:** CSV parsing and data import with multi-encoding support

**Documented Methods:**
- `process_csv_chunk()` - Multi-threaded CSV processing
- `batch_import_csv()` - Process multiple files concurrently
- `import_subject_scores_from_file()` - Main CSV import function (extensive)
- `_normalize_key()` - Fuzzy column matching normalization
- `_parse_float()` - Safe float conversion with null handling
- `_find_column_name()` - Fuzzy column name matching
- `import_subject_scores_from_csv()` - Disk file import wrapper
- `export_to_json()` - Data export to JSON

**Key Learning Points:**
- Multi-encoding detection (UTF-8-BOM, UTF-8, Latin-1, CP1252)
- CSV dialect auto-detection
- Quote-wrapped line handling for Windows compatibility
- Fuzzy matching for flexible CSV formats
- Empty value preservation (None vs 0)
- CSV data aggregation and calculations

---

#### 3. **server/api_server.py** 
**Status:** Already has extensive comments in original
**Purpose:** Flask REST API endpoints for authentication and course management

**Key Routes:**
- POST `/api/signup` - User registration
- POST `/api/auth` - User login
- GET `/api/courses` - Fetch user courses
- POST `/api/courses` - Create course
- PUT `/api/courses/{id}` - Update course
- POST `/api/import-subject-scores` - CSV import

**Note:** Code already contains inline comments explaining CORS, password hashing, and endpoint logic

---

### Frontend Files (React/JavaScript)

#### 4. **client/src/App.jsx** ✓
**Status:** Fully documented with detailed comments
**Purpose:** Root React component managing navigation, auth, and state

**Documented Elements:**
- State variables with explanations
- useEffect for course loading
- `handleSignIn()` - Login handler
- `handleSignUp()` - Registration handler
- `handleSignOut()` - Logout handler
- `handleUploadCsvSelected()` - File selection
- `handleProcessCsvUpload()` - CSV upload and processing
- `handleSaveCourse()` - Course save logic
- `handleOpenCourse()` / `handleEditCourse()` - Navigation handlers

**Key Learning Points:**
- React hooks (useState, useEffect)
- State management patterns
- Axios async API calls
- Form data handling (FormData for file uploads)
- Navigation state machine

---

#### 5. **client/src/components/CourseDetail.jsx** ✓
**Status:** Fully documented with detailed comments
**Purpose:** Display course with component score inputs and grade calculation

**Documented Elements:**
- Component props and purpose
- State management for inputs
- CSV pre-population logic
- Real-time grade calculation
- Grade suggestion algorithm
- `handleInputChange()` - Score input handler
- `handleCalculate()` - Suggestion calculator

**Key Learning Points:**
- React hooks (useState, useMemo)
- Form state management
- Complex calculation logic
- Weighted grade formula
- Memoization for performance

---

#### 6. **client/src/components/Dashboard.jsx** ✓
**Status:** Partially documented with section comments
**Purpose:** Main page showing courses and CSV upload interface

**Documented Elements:**
- Component props
- File input handler
- Header with user profile
- Action buttons
- Course list layout
- CSV upload status display

**Key Learning Points:**
- Props destructuring for many callback functions
- Conditional rendering
- File input handling
- State-based UI updates

---

#### 7. **client/src/components/Login.jsx**
**Status:** Self-explanatory form component
**Purpose:** Sign in and sign up forms for authentication

---

#### 8. **client/src/components/CourseCreator.jsx**
**Status:** Self-explanatory form component
**Purpose:** Manual course and component creation form

---

## 📖 Documentation Files

### 1. **CODEBASE_GUIDE.md** ✓✓✓
**Comprehensive Architecture Guide Including:**
- Project structure overview
- Database schema with diagrams
- Backend architecture explanation
- Frontend component hierarchy
- Data flow diagrams (CSV import, grade calculation)
- Security features explanation
- Important code concepts with examples
- Common issues and solutions
- Running instructions
- Development notes
- Testing guidelines

**This is your PRIMARY REFERENCE for understanding the system**

---

## 🔍 How to Use This Documentation

### For Learning a Specific File:
1. **Read the file header comment** - Explains purpose and features
2. **Read method docstrings** - Explains inputs, outputs, and logic
3. **Read inline comments** - Explains why specific code exists
4. **Reference CODEBASE_GUIDE.md** - Understands context in overall system

### For Understanding a Feature:
1. **Find feature in CODEBASE_GUIDE.md** - High-level explanation
2. **Follow data flow diagrams** - Trace through system
3. **Look at specific files** - See implementation details
4. **Check inline comments** - Understand code decisions

### For Debugging:
1. **Check "Common Issues & Solutions"** in CODEBASE_GUIDE.md
2. **Look at related database.py code** - Data storage logic
3. **Check data_manager.py code** - CSV parsing issues
4. **Look at React component state** - Frontend rendering issues

---

## 📝 Code Comment Standards Used

### File Header
```python
# ==========================================
# MODULE NAME - path/to/file.py
# ==========================================
# Description of what this file does
# Key features
```

### Class Header
```python
class ClassName:
    """
    Multi-line docstring explaining:
    - Purpose
    - Key features
    - Main responsibilities
    """
```

### Function Header
```python
def function_name(param1, param2):
    """
    Description of what function does
    
    Args:
        param1: Type and description
        param2: Type and description
        
    Returns:
        ReturnType: Description of return value
        
    Raises:
        ExceptionType: When this exception occurs
        
    Example:
        function_name(value1, value2)  # Returns X
    """
```

### Inline Comments
```python
# Section headers mark logical blocks
variable = value  # Brief explanation of why

# More complex logic gets multi-line explanation
# explaining the algorithm or non-obvious behavior
```

---

## 🎯 Key Takeaways for Understanding the Codebase

### Authentication Flow
1. User enters credentials in Login.jsx
2. App.jsx sends to `/api/auth` or `/api/signup`
3. Backend (api_server.py) validates and hashes password
4. Database (database.py) stores or verifies user
5. User object returned and stored in React state

### CSV Import Flow
1. User selects CSV in Dashboard.jsx
2. App.jsx uploads to `/api/import-subject-scores`
3. data_manager.py parses with multi-encoding support
4. Columns matched with fuzzy matching
5. Scores extracted and preserved as-is (null vs 0)
6. Database creates courses with components
7. API returns with database IDs
8. Frontend updates course list with pre-filled scores

### Grade Calculation Flow
1. User views course in CourseDetail.jsx
2. Component loads with CSV scores pre-filled
3. User enters missing scores
4. Real-time calculation updates grade percentage
5. User clicks Calculate for suggestions
6. Algorithm distributes needed points proportionally
7. Display if passing or how many points needed

---

## 🔗 Related Documentation

- **CODEBASE_GUIDE.md** - Main architecture guide
- **Code comments** - In-file documentation
- **Test files** (tests/ folder) - Usage examples
- **Conversation history** - Problem-solving examples

---

## ❓ Quick Questions Answered

**Q: Where is user authentication handled?**
A: `server/database.py` (hashing/verifying) and `server/api_server.py` (routes)

**Q: How are CSV files parsed?**
A: `server/data_manager.py` with multi-encoding support and fuzzy column matching

**Q: How is grade calculated?**
A: `client/src/components/CourseDetail.jsx` with weighted formula

**Q: Where is data stored?**
A: SQLite database (`server/acadence.db`) with schema in `server/database.py`

**Q: How do courses get pre-filled scores?**
A: CSV imported → database stores scores → API returns with IDs → React pre-populates

---

*Documentation Last Updated: June 23, 2026*
