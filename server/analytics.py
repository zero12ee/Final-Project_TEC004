# server/analytics.py
import pandas as pd
from sklearn.linear_model import LinearRegression

class AcademicAnalytics:
    def __init__(self, db_name):
        self.db_name = db_name
        self.model = LinearRegression()

    def train_prediction_model(self, csv_path):
        # Load data
        df = pd.read_csv(csv_path)
        X = df[['midterm_score', 'attendance_rate', 'assignment_rate']]
        y = df['final_grade']
        
        # Train model
        self.model.fit(X, y)
        
        # Score model
        score = self.model.score(X, y)
        print(f"Model trained with R^2 score: {score:.2f}")