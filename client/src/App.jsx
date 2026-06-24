/**
 * Main Application Component
 * 
 * App.jsx is the root component that manages:
 * - User authentication (sign in/sign up)
 * - View navigation (dashboard, course detail, course editor)
 * - Course management (create, update, fetch)
 * - CSV file upload and import
 * - API communication with Flask backend
 * 
 * State Management:
 * - user: Current logged-in user
 * - view: Current page (dashboard, detail, edit, create)
 * - courses: User's courses list
 * - selectedCourse: Course being viewed/edited
 * - authError: Authentication error messages
 * - pendingUploadFile: CSV file selected for upload
 * - uploadPerformanceExpected: Target score for courses
 * - uploadResult: Result of CSV import
 * - uploadError: CSV import errors
 * - isUploadingFile: Upload in-progress flag
 */

import { useEffect, useState } from 'react';
import axios from 'axios';
import './App.css';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import CourseCreator from './components/CourseCreator';
import CourseDetail from './components/CourseDetail';

// Backend API endpoint
const API_BASE = 'http://localhost:5000/api';

function App() {
  // ================== STATE VARIABLES ==================
  
  /** Current logged-in user: {id, username, email} */
  const [user, setUser] = useState(null);
  
  /** Current view: 'dashboard' | 'detail' | 'edit' | 'create' */
  const [view, setView] = useState('dashboard');
  
  /** List of user's courses */
  const [courses, setCourses] = useState([]);
  
  /** Course being viewed or edited */
  const [selectedCourse, setSelectedCourse] = useState(null);
  
  /** Authentication error message */
  const [authError, setAuthError] = useState('');
  
  /** CSV file pending upload */
  const [pendingUploadFile, setPendingUploadFile] = useState(null);
  
  /** Expected total score for imported courses */
  const [uploadPerformanceExpected, setUploadPerformanceExpected] = useState(100);
  
  /** Result from CSV import */
  const [uploadResult, setUploadResult] = useState(null);
  
  /** CSV import error message */
  const [uploadError, setUploadError] = useState('');
  
  /** Flag indicating CSV upload is in progress */
  const [isUploadingFile, setIsUploadingFile] = useState(false);

  // ================== EFFECTS ==================
  
  /**
   * Load user's courses when user logs in/logs out
   * Called whenever user state changes
   */
  useEffect(() => {
    if (!user) {
      setCourses([]);
      return;
    }

    const loadCourses = async () => {
      try {
        const response = await axios.get(`${API_BASE}/courses`, {
          params: { user_id: user.id },
        });
        setCourses(response.data.courses || []);
      } catch (error) {
        console.error('Failed to load courses', error);
      }
    };

    loadCourses();
  }, [user]);

  // ================== AUTH HANDLERS ==================

  /**
   * Handle user sign-in (login)
   * Sends credentials to backend for authentication
   * 
   * @param {Object} credentials - {id: username, password}
   */
  const handleSignIn = async (credentials) => {
    setAuthError('');
    try {
      const response = await axios.post(`${API_BASE}/auth`, credentials);
      setUser(response.data.user);
      setView('dashboard');
    } catch (error) {
      setAuthError(error.response?.data?.error || 'Sign in failed.');
    }
  };

  /**
   * Handle user sign-up (account creation)
   * Sends registration data to backend
   * 
   * @param {Object} credentials - {id: username, email, password}
   */
  const handleSignUp = async (credentials) => {
    setAuthError('');
    try {
      const response = await axios.post(`${API_BASE}/signup`, credentials);
      // Store the returned user object and show the dashboard.
      setUser(response.data.user);
      setView('dashboard');
    } catch (error) {
      setAuthError(error.response?.data?.error || 'Sign up failed.');
    }
  };

  /**
   * Handle user sign-out (logout)
   * Clears user data and resets to dashboard view
   */
  const handleSignOut = () => {
    setUser(null);
    setSelectedCourse(null);
    setView('dashboard');
  };

  // ================== CSV UPLOAD HANDLERS ==================

  /**
   * Handle CSV file selection
   * Stores file for later processing
   * 
   * @param {File} file - CSV file selected by user
   */
  const handleUploadCsvSelected = (file) => {
    setPendingUploadFile(file);
    setUploadResult(null);
    setUploadError('');
  };

  /**
   * Process CSV file upload and create courses
   * 
   * Steps:
   * 1. Create FormData with file and user ID
   * 2. Send to /import-subject-scores endpoint
   * 3. Parse response for created courses
   * 4. Add new courses to state
   * 5. Clear upload UI
   * 
   * Returns courses with pre-filled component scores from CSV
   */
  const handleProcessCsvUpload = async () => {
    if (!pendingUploadFile) return;
    setIsUploadingFile(true);
    setUploadError('');
    setUploadResult(null);

    try {
      const formData = new FormData();
      formData.append('csv_file', pendingUploadFile);
      formData.append('defaultExpectedTotal', uploadPerformanceExpected.toString());

      formData.append('user_id', user.id);
      const response = await axios.post(`${API_BASE}/import-subject-scores`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      const result = response.data;
      setUploadResult(result.parsed || result);

      if (user && Array.isArray(result.createdCourses)) {
        setCourses((prev) => [...prev, ...result.createdCourses]);
      }

      setPendingUploadFile(null);
      setUploadPerformanceExpected(100);
    } catch (error) {
      setUploadError(error.response?.data?.error || 'CSV upload failed.');
      console.error('CSV upload failed', error);
    } finally {
      setIsUploadingFile(false);
    }
  };

  const handleSaveCourse = async (course) => {
    if (!user) return;

    try {
      if (course.id) {
        const response = await axios.put(`${API_BASE}/courses/${course.id}`, {
          ...course,
          user_id: user.id,
        });
        const updatedCourse = response.data.course;
        setCourses((prev) => prev.map((item) => (item.id === updatedCourse.id ? updatedCourse : item)));
      } else {
        const response = await axios.post(`${API_BASE}/courses`, {
          ...course,
          user_id: user.id,
        });
        setCourses((prev) => [...prev, response.data.course]);
      }
      setSelectedCourse(null);
      setView('dashboard');
    } catch (error) {
      console.error('Failed to save course', error);
    }
  };

  const handleOpenCourse = (course) => {
    setSelectedCourse(course);
    setView('detail');
  };

  const handleEditCourse = (course) => {
    setSelectedCourse(course);
    setView('edit');
  };

  const handleBackToDashboard = () => {
    setSelectedCourse(null);
    setView('dashboard');
  };

  return (
    <div className="app-shell">
      {!user ? (
        <Login onSignIn={handleSignIn} onSignUp={handleSignUp} authError={authError} />
      ) : view === 'dashboard' ? (
        <Dashboard
          user={user}
          courses={courses}
          onCreateCourse={() => setView('create')}
          onOpenCourse={handleOpenCourse}
          onEditCourse={handleEditCourse}
          onSignOut={handleSignOut}
          pendingUploadFile={pendingUploadFile}
          uploadPerformanceExpected={uploadPerformanceExpected}
          onSelectUploadCsv={handleUploadCsvSelected}
          onChangeUploadPerformance={setUploadPerformanceExpected}
          onProcessUpload={handleProcessCsvUpload}
          uploadResult={uploadResult}
          uploadError={uploadError}
          isUploadingFile={isUploadingFile}
        />
      ) : view === 'create' ? (
        <CourseCreator onSave={handleSaveCourse} onCancel={handleBackToDashboard} />
      ) : view === 'edit' ? (
        <CourseCreator course={selectedCourse} onSave={handleSaveCourse} onCancel={handleBackToDashboard} />
      ) : (
        <CourseDetail user={user} course={selectedCourse} onBack={handleBackToDashboard} />
      )}
    </div>
  );
}

export default App;
