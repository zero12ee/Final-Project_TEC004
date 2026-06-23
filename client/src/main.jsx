import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import { useState } from 'react';
import CourseCreator from './components/CourseCreator';

function App() {
    const [view, setView] = useState('DASHBOARD'); // 'DASHBOARD' or 'CREATE'

    const handleSaveCourse = (data) => {
        console.log("Saving Course to Database:", data);
        // Here you will add your axios.post('/api/courses', data)
        setView('DASHBOARD');
    };

    return (
        <div className="container">
            {view === 'DASHBOARD' ? (
                <div>
                    <h1>My Courses</h1>
                    <button onClick={() => setView('CREATE')}>Create New Course</button>
                    {/* Map your courses here */}
                </div>
            ) : (
                <CourseCreator onSave={handleSaveCourse} />
            )}
        </div>
    );
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
