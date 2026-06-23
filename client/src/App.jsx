import { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [formData, setFormData] = useState({
    student_name: '',
    midterm_score: '',
    attendance_rate: '',
    assignment_rate: ''
  });
  
  const [predictionResult, setPredictionResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setPredictionResult(null);

    try {
      const response = await axios.post('http://localhost:5000/api/predict', formData);
      setPredictionResult(response.data);
    } catch (error) {
      console.error("Error making prediction:", error);
      setPredictionResult({ error: "Failed to connect to the server." });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>Acadence Grade Predictor</h1>
      <p>Enter a student's current progress to predict their final grade.</p>

      <form onSubmit={handleSubmit} className="form-card">
        <div className="form-group">
          <label>Student Name:</label>
          <input 
            type="text" 
            name="student_name" 
            value={formData.student_name} 
            onChange={handleChange} 
            required 
          />
        </div>

        <div className="form-group">
          <label>Midterm Score (0-100):</label>
          <input 
            type="number" 
            name="midterm_score" 
            value={formData.midterm_score} 
            onChange={handleChange} 
            min="0" max="100" 
            required 
          />
        </div>

        <div className="form-group">
          <label>Attendance Rate (0-100%):</label>
          <input 
            type="number" 
            name="attendance_rate" 
            value={formData.attendance_rate} 
            onChange={handleChange} 
            min="0" max="100" 
            required 
          />
        </div>

        <div className="form-group">
          <label>Assignment Completion Rate (0-100%):</label>
          <input 
            type="number" 
            name="assignment_rate" 
            value={formData.assignment_rate} 
            onChange={handleChange} 
            min="0" max="100" 
            required 
          />
        </div>

        <button type="submit" disabled={loading}>
          {loading ? "Predicting..." : "Predict Final Grade"}
        </button>
      </form>

      {predictionResult && !predictionResult.error && (
        <div className={`result-card ${predictionResult.is_at_risk ? 'risk' : 'safe'}`}>
          <h2>Prediction for {predictionResult.student_name}</h2>
          <p><strong>Predicted Final Score:</strong> {predictionResult.predicted_score}</p>
          <p><strong>Status:</strong> {predictionResult.is_at_risk ? "⚠️ AT RISK OF FAILING" : "✅ ON TRACK TO PASS"}</p>
        </div>
      )}

      {predictionResult && predictionResult.error && (
        <div className="result-card risk">
          <p>{predictionResult.error}</p>
        </div>
      )}
    </div>
  );
}

export default App;

import Login from './components/Login';
import Dashboard from './components/Dashboard';

function App() {
  const [user, setUser] = useState(null);
  const [view, setView] = useState('DASHBOARD');

  if (!user) return <Login onLogin={setUser} />;
  return <Dashboard user={user} />;
}
export default App;