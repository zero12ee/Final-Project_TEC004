# ==========================================
# Author: Pham Gia Bao (Student ID: AUS15065)
# Project ID: TEC004/05
# Description: SP1 - OOP Models and Class Hierarchy
# ==========================================

from abc import ABC, abstractmethod
from typing import List, Dict

class Person(ABC):
    def __init__(self, person_id: str, name: str, email: str):
        self.person_id = person_id
        self.name = name
        self.email = email

class Student(Person):
    def __init__(self, person_id: str, name: str, email: str, major: str):
        super().__init__(person_id, name, email)
        self.major = major
        self.enrolled_courses = []

class Instructor(Person):
    def __init__(self, person_id: str, name: str, email: str, department: str):
        super().__init__(person_id, name, email)
        self.department = department

class GradeBook(ABC):
    @abstractmethod
    def calculate_final_grade(self, scores: Dict[str, float]) -> float:
        pass

class WeightedGrade(GradeBook):
    def __init__(self, weights: Dict[str, float]):
        self.weights = weights

    def calculate_final_grade(self, scores: Dict[str, float]) -> float:
        weighted_scores = map(lambda item: item[1] * self.weights.get(item[0], 0), scores.items())
        return sum(weighted_scores)

class PassFailGrade(GradeBook):
    def __init__(self, passing_threshold: float = 50.0):
        self.passing_threshold = passing_threshold

    def calculate_final_grade(self, scores: Dict[str, float]) -> str:
        average = sum(scores.values()) / len(scores) if scores else 0
        return "Pass" if average >= self.passing_threshold else "Fail"

class Course:
    def __init__(self, course_id: str, title: str, instructor: Instructor, grading_scheme: GradeBook):
        self.course_id = course_id
        self.title = title
        self.instructor = instructor
        self.grading_scheme = grading_scheme
        self.enrollments = []