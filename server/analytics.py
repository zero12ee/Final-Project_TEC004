# ==========================================
# Author: Pham Gia Bao (Student ID: AUS15065)
# Project ID: TEC004/05
# Description: SP4, SP5, SP6 - Analytics, Visualization & AI
# ==========================================

import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

class AcademicAnalytics:
    def __init__(self, db_path="acadence.db"):
        self.conn = sqlite3.connect(db_path)

    def load_data(self) -> pd.DataFrame:
        query = '''
            SELECT s.person_id, s.name, g.assessment_type, g.score
            FROM Students s
            JOIN Enrollments e ON s.person_id = e.student_id
            JOIN Grades g ON e.enrollment_id = g.enrollment_id
        '''
        return pd.read_sql_query(query, self.conn)

    def generate_visualizations(self):
        df = self.load_data()
        if df.empty:
            return
        
        pivot_df = df.pivot_table(index='person_id', columns='assessment_type', values='score')
        
        if 'final' in pivot_df.columns:
            plt.figure(figsize=(8, 5))
            plt.hist(pivot_df['final'].dropna(), bins=10, color='skyblue', edgecolor='black')
            plt.title('Final Exam Grade Distribution')
            plt.xlabel('Score')
            plt.ylabel('Number of Students')
            plt.savefig('grade_distribution.png')
            plt.close()

    def train_prediction_model(self, data_csv_path: str):
        df = pd.read_csv(data_csv_path)
        X = df[['midterm_score', 'attendance_rate', 'assignment_rate']]
        y = df['final_grade']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = LinearRegression()
        model.fit(X_train, y_train)
        
        self.model = model
        print(f"Model trained with R^2 score: {model.score(X_test, y_test):.2f}")
        return model

    def identify_at_risk_students(self, current_students_df: pd.DataFrame, passing_threshold: float = 50.0):
        if not hasattr(self, 'model'):
            raise ValueError("Model must be trained first.")
            
        X_current = current_students_df[['midterm_score', 'attendance_rate', 'assignment_rate']]
        predictions = self.model.predict(X_current)
        
        current_students_df['predicted_final'] = predictions
        at_risk = current_students_df[current_students_df['predicted_final'] < passing_threshold]
        
        return at_risk[['student_name', 'predicted_final']].to_dict(orient='records')