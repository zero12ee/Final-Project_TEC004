import { useEffect, useState } from 'react';
import axios from 'axios';
import './App.css';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import CourseCreator from './components/CourseCreator';
import CourseDetail from './components/CourseDetail';

const API_BASE = 'http://localhost:5000/api';

function App() {
  const [user, setUser] = useState(null);
  const [view, setView] = useState('dashboard');
  const [courses, setCourses] = useState([]);
  const [selectedCourse, setSelectedCourse] = useState(null);
  const [authError, setAuthError] = useState('');

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

  const handleSignOut = () => {
    setUser(null);
    setSelectedCourse(null);
    setView('dashboard');
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
