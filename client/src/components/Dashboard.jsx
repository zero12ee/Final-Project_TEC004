import React from 'react';

const Dashboard = ({ user, courses, onCreateCourse, onOpenCourse, onEditCourse, onSignOut }) => {
  const displayName = user.username || String(user.id || 'User');

  return (
    <div className="container">
      <div className="topbar">
        <span className="topbar-brand">Performance Tracker</span>
        <div className="topbar-user">
          <div className="avatar">{displayName.charAt(0).toUpperCase()}</div>
          <span>{displayName}</span>
          <button type="button" className="btn-logout" onClick={onSignOut}>Sign Out</button>
        </div>
      </div>

      <div className="main-content">
        <p className="page-title">My Courses</p>
        <div className="actions-row">
          <button type="button" className="btn-primary" onClick={onCreateCourse}>+ Create New Course</button>
        </div>

        <div className="dashboard-grid">
          {courses.length === 0 ? (
            <div className="page-card">
              <p>No courses yet. Create one to get started.</p>
            </div>
          ) : (
            courses.map((course) => (
              <div key={course.id} className="course-card">
                <div className="course-info">
                  <h2>{course.name}</h2>
                  <p>{course.components.length} components</p>
                </div>
                <div className="course-actions">
                  <button type="button" className="btn-primary" onClick={() => onOpenCourse(course)}>Open</button>
                  <button type="button" className="secondary small" onClick={() => onEditCourse(course)}>Edit</button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
