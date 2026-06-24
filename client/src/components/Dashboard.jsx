import React from 'react';

/**
 * Dashboard Component
 * 
 * Main page displaying:
 * - User profile and logout button
 * - Buttons to create new course or upload CSV
 * - List of existing courses with open/edit/delete options
 * - CSV upload progress and results
 * 
 * Props (from App.jsx):
 * - user: Current user object
 * - courses: Array of user's courses
 * - Callbacks: onCreateCourse, onOpenCourse, onEditCourse, onSignOut
 * - CSV Upload: onSelectUploadCsv, onChangeUploadPerformance, onProcessUpload
 * - Upload State: pendingUploadFile, uploadPerformanceExpected, uploadResult, uploadError, isUploadingFile
 */
const Dashboard = ({ 
  user, 
  courses, 
  onCreateCourse, 
  onOpenCourse, 
  onEditCourse, 
  onSignOut, 
  pendingUploadFile, 
  uploadPerformanceExpected, 
  onSelectUploadCsv, 
  onChangeUploadPerformance, 
  onProcessUpload, 
  uploadResult, 
  uploadError, 
  isUploadingFile 
}) => {
  // ================== HELPERS ==================
  
  /** Get display name (username or user ID) */
  const displayName = user.username || String(user.id || 'User');

  /**
   * Handle file input change
   * Triggers onSelectUploadCsv callback with selected file
   */
  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      onSelectUploadCsv(file);
    }
  };

  return (
    <div className="container">
      {/* ================== HEADER ==================*/}
      <div className="topbar">
        <span className="topbar-brand">Performance Tracker</span>
        <div className="topbar-user">
          {/* User avatar (first letter) */}
          <div className="avatar">{displayName.charAt(0).toUpperCase()}</div>
          <span>{displayName}</span>
          <button type="button" className="btn-logout" onClick={onSignOut}>Sign Out</button>
        </div>
      </div>

      {/* ================== MAIN CONTENT ==================*/}
      <div className="main-content">
        <p className="page-title">My Courses</p>
        
        {/* ================== ACTION BUTTONS ==================*/}
        <div className="actions-row">
          {/* Create new course button */}
          <button type="button" className="btn-primary" onClick={onCreateCourse}>
            + Create New Course
          </button>
          
          {/* CSV upload button with file input */}
          <label className="csv-upload-button btn-secondary">
            <span>
              {isUploadingFile ? 'Uploading...' : pendingUploadFile ? pendingUploadFile.name : 'Upload CSV'}
            </span>
            <input 
              type="file" 
              accept=".csv" 
              onChange={handleFileChange} 
              disabled={isUploadingFile} 
            />
          </label>
        </div>

        {pendingUploadFile && (
          <div className="page-card">
            <div className="form-group">
              <label>Performance Expectation (%)</label>
              <input
                type="number"
                min="0"
                max="100"
                value={uploadPerformanceExpected}
                onChange={(e) => onChangeUploadPerformance(Number(e.target.value))}
              />
            </div>
            <div className="actions-row">
              <button className="btn-primary" onClick={onProcessUpload} disabled={isUploadingFile}>
                {isUploadingFile ? 'Processing...' : 'Process CSV and Create Courses'}
              </button>
            </div>
          </div>
        )}

        {uploadError && <div className="alert alert-error">{uploadError}</div>}
        {uploadResult && (
          <div className="alert alert-success">
            <strong>CSV Imported:</strong> {uploadResult.subjects?.length || 0} subjects processed.
          </div>
        )}

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
