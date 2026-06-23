# ==========================================
# Author: Pham Gia Bao (Student ID: AUS15065)
# Project ID: TEC004/05
# Description: Flask API Server for React Frontend
# ==========================================
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from analytics import AcademicAnalytics
import os
from database import Database

app = Flask(__name__)
# Allow the React frontend to communicate with this server
CORS(app)
db = Database()

print("Initializing Analytics and Training Model...")
analytics = AcademicAnalytics("acadence.db")

# Ensure training data exists
if not os.path.exists("data/historical_data.csv"):
    historical_data = pd.DataFrame({
        'midterm_score': [85, 45, 90, 60, 75, 82, 50, 95, 40, 70, 88, 55],
        'attendance_rate': [90, 60, 95, 70, 80, 85, 55, 98, 45, 75, 92, 65],
        'assignment_rate': [100, 50, 100, 60, 85, 90, 40, 100, 30, 80, 95, 60],
        'final_grade': [88, 40, 92, 65, 78, 85, 45, 96, 35, 72, 89, 58]
    })
    os.makedirs("data", exist_ok=True)
    historical_data.to_csv("data/historical_data.csv", index=False)

analytics.train_prediction_model("data/historical_data.csv")
print("Server ready to receive data on port 5000.")

@app.route('/api/predict', methods=['POST'])
def predict_grade():
    try:
        data = request.json
        
        current_student = pd.DataFrame({
            'student_name': [data.get('student_name')],
            'midterm_score': [float(data.get('midterm_score'))],
            'attendance_rate': [float(data.get('attendance_rate'))],
            'assignment_rate': [float(data.get('assignment_rate'))]
        })
        
        passing_threshold = 50.0
        X_current = current_student[['midterm_score', 'attendance_rate', 'assignment_rate']]
        prediction = analytics.model.predict(X_current)[0]
        
        is_at_risk = bool(prediction < passing_threshold)
        
        return jsonify({
            "student_name": data.get('student_name'),
            "predicted_score": round(prediction, 2),
            "is_at_risk": is_at_risk
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/calculate', methods=['POST'])
def calculate_grade():
    data = request.json
    components = data.get('components') # List of {name, weight, max_points, input_points}
    target_percentage = 60.0 # Pass requirement
    
    total_secured = 0
    remaining_weight = 0
    
    for comp in components:
        # If user input a score, calculate the earned percentage
        if comp['input_points'] is not None and comp['input_points'] != "":
            pts = float(comp['input_points'])
            total_secured += (pts / comp['max_points']) * comp['weight']
        else:
            # If empty, this component is "missing" and needs a prediction
            remaining_weight += comp['weight']
    
    # Calculate predicted points needed
    needed = target_percentage - total_secured
    predicted_avg_needed = (needed / remaining_weight) * 100 if remaining_weight > 0 else 0
    
    return jsonify({
        "current_total": round(total_secured, 2),
        "suggested_score_needed": round(predicted_avg_needed, 2),
        "is_passing": total_secured >= target_percentage
    })

@app.route('/api/auth', methods=['POST'])
def auth():
    data = request.json
    # Simple auth check (In production, use hashed passwords)
    return jsonify({"status": "success", "user_id": 1}) 

@app.route('/api/courses', methods=['POST'])
def create_course():
    data = request.json
    # Insert Course and its Components into DB...
    return jsonify({"status": "created"})

@app.route('/api/predict', methods=['POST'])
def calculate_grade():
    data = request.json
    components = data.get('components')
    target = 60.0
    
    current_earned = sum((c['input_points'] / c['max_points']) * c['weight'] for c in components if c['input_points'])
    remaining_weight = sum(c['weight'] for c in components if not c['input_points'])
    
    suggested = ((target - current_earned) / remaining_weight) * 100 if remaining_weight > 0 else 0
    
    return jsonify({
        "current_total": round(current_earned, 2),
        "suggested_score_needed": round(suggested, 2),
        "is_passing": current_earned >= target
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)