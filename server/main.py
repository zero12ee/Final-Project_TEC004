# ==========================================
# Author: Nguyen Luong Nhat (Student ID: AUS14988)
# Project ID: TEC004/05
# Description: Main entry point for the Application
# ==========================================

import os
import pandas as pd
from database import DatabaseManager
from data_manager import DataManager
from analytics import AcademicAnalytics

def create_sample_data():
    if not os.path.exists("data"):
        os.makedirs("data")
        
    sample_grades = """student_id,assessment_type,score\nS001,midterm,85\nS001,attendance_rate,90\nS001,assignment_rate,100\nS001,final,88\nS002,midterm,45\nS002,attendance_rate,60\nS002,assignment_rate,50\nS002,final,40"""
    
    with open("data/class_1_grades.csv", "w") as f:
        f.write(sample_grades)

def main():
    print("=== Starting Project System ===")
    
    print("\n[1] Initializing SQLite Database...")
    db = DatabaseManager("acadence.db")
    
    print("\n[2] Running Multi-threaded Data Import...")
    create_sample_data()
    data_mgr = DataManager()
    
    files_to_process = ["data/class_1_grades.csv"] 
    imported_data = data_mgr.batch_import_csv(files_to_process)
    
    data_mgr.export_to_json(imported_data, "data/backup_export.json")
    print(f"Imported {len(imported_data)} records and backed up to JSON.")

    print("\n[3] Generating Analytics and Visualizations...")
    analytics = AcademicAnalytics("acadence.db")
    try:
        analytics.generate_visualizations()
        print("Visualizations generated successfully (saved as PNGs).")
    except Exception as e:
        print(f"Skipping visualization: {e}")

    print("\n[4] Training AI Grade Prediction Model...")
    # Expanded dummy dataset to avoid the R^2 math warning
    historical_data = pd.DataFrame({
        'midterm_score': [85, 45, 90, 60, 75, 82, 50, 95, 40, 70, 88, 55],
        'attendance_rate': [90, 60, 95, 70, 80, 85, 55, 98, 45, 75, 92, 65],
        'assignment_rate': [100, 50, 100, 60, 85, 90, 40, 100, 30, 80, 95, 60],
        'final_grade': [88, 40, 92, 65, 78, 85, 45, 96, 35, 72, 89, 58]
    })
    historical_data.to_csv("data/historical_data.csv", index=False)
    
    analytics.train_prediction_model("data/historical_data.csv")
    
    current_students = pd.DataFrame({
        'student_name': ['Alice', 'Bob'],
        'midterm_score': [82, 42],
        'attendance_rate': [88, 55],
        'assignment_rate': [95, 40]
    })
    
    at_risk = analytics.identify_at_risk_students(current_students, passing_threshold=50.0)
    print("\n--- AT-RISK STUDENTS ALERT ---")
    for student in at_risk:
        print(f"WARNING: {student['student_name']} is predicted to score {student['predicted_final']:.2f} (Failing)")

    print("\n=== System Run Complete ===")

if __name__ == "__main__":
    main()
