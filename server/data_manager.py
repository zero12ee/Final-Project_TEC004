# ==========================================
# CSV DATA MANAGER - server/data_manager.py
# ==========================================
# Author: Pham Gia Bao (Student ID: AUS15065)
# Project ID: TEC004/05
# Description: Handles CSV import and parsing for course/component data
# 
# Key Features:
#   - Multi-encoding support (UTF-8-BOM, UTF-8, Latin-1, CP1252)
#   - Automatic dialect detection (CSV format detection)
#   - Quote-wrapped line handling (Windows CRLF compatible)
#   - Fuzzy column matching (flexible header detection)
#   - Student ID extraction and tracking
#   - Empty value handling (distinguishes between 0 and null)
#   - Data aggregation by subject/course
#   - JSON export capability

import csv
import io
import json
import threading
import time
from typing import List

def time_logger(func):
    """Decorator to log execution time of functions"""
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"[{func.__name__}] Executed in {time.time() - start:.4f} seconds")
        return result
    return wrapper

class DataManager:
    """
    Manager for parsing and processing CSV files containing course/component data
    """
    
    @staticmethod
    def process_csv_chunk(file_path: str, results_list: List):
        """
        Process a single CSV file and append results to shared list
        Used for multi-threaded batch import
        
        Args:
            file_path: Path to CSV file
            results_list: Shared list to append results to
        """
        try:
            with open(file_path, mode='r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                cleaned_data = list(map(lambda row: {k: v.strip() for k, v in row.items()}, reader))
                results_list.extend(cleaned_data)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    @time_logger
    def batch_import_csv(self, file_paths: List[str]) -> List[dict]:
        """
        Import multiple CSV files using separate threads
        
        Args:
            file_paths: List of paths to CSV files
            
        Returns:
            list: Combined data from all files
        """
        threads = []
        combined_results = []
        
        for path in file_paths:
            thread = threading.Thread(target=self.process_csv_chunk, args=(path, combined_results))
            threads.append(thread)
            thread.start()
            
        for thread in threads:
            thread.join()  # Wait for all threads to complete
            
        return combined_results

    def import_subject_scores_from_file(
        self,
        file_obj,
        expected_totals: dict = None,
        default_expected_total: float = 100.0,
    ) -> dict:
        """
        Parse CSV file and extract course/component data
        
        Features:
        - Multi-encoding detection (handles UTF-8-BOM, UTF-8, Latin-1, CP1252)
        - Automatic CSV dialect detection
        - Quote-wrapped line handling for Windows line endings
        - Flexible column name matching (fuzzy matching)
        - Student ID extraction
        - Empty value preservation (None instead of 0)
        - Data aggregation by subject/course
        
        CSV Format Expected:
        Headers: Student_ID, Course_Name, Component_Name, Weight_Percentage, Max_Points, Points_Earned
        
        Args:
            file_obj: File object or BytesIO with CSV data
            expected_totals: Dict mapping course names to expected total scores
            default_expected_total: Default expectation if not in expected_totals
            
        Returns:
            dict: Parsed data with structure:
            {
              'sourceFile': str,
              'subjects': [
                {
                  'subject': str (course name),
                  'studentIds': [str],
                  'components': [{
                    'name': str,
                    'score': float or None,
                    'maxPoints': float,
                    'weight': float
                  }],
                  'expectedTotal': float,
                  'percentage': float,
                  'meetsExpectation': bool,
                  'totalScore': float,
                  'totalMax': float,
                  'weightedScore': float
                }
              ],
              'summary': {
                'grandTotal': float,
                'grandMax': float,
                'overallPercentage': float
              }
            }
            
        Raises:
            ValueError: If file cannot be decoded or parsed
        """
        # Read file content and handle encoding
        if hasattr(file_obj, 'read'):
            content = file_obj.read()
            if isinstance(content, bytes):
                # Try multiple encodings in order of preference
                encodings = ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']
                decoded = None
                for encoding in encodings:
                    try:
                        decoded = content.decode(encoding)
                        break
                    except (UnicodeDecodeError, AttributeError):
                        continue
                if decoded is None:
                    raise ValueError("Could not decode CSV file with any supported encoding")
                content = decoded
            file_obj = io.StringIO(content)

        # Read content to detect dialect
        content_str = file_obj.read()
        
        # Handle edge case: entire lines wrapped in quotes
        lines = content_str.split('\n')
        processed_lines = []
        for line in lines:
            # Remove trailing whitespace before checking quotes
            line = line.rstrip()
            if line.startswith('"') and line.endswith('"'):
                # Remove surrounding quotes
                line = line[1:-1]
            processed_lines.append(line)
        content_str = '\n'.join(processed_lines)
        
        file_obj = io.StringIO(content_str)
        
        # Auto-detect CSV dialect (AFTER removing quotes)
        dialect = 'excel'  # Default dialect
        try:
            sample = '\n'.join(content_str.split('\n')[:5])
            detected = csv.Sniffer().sniff(sample, delimiters=',;\t|')
            # Validate the detected dialect
            if detected and hasattr(detected, 'delimiter') and detected.delimiter in [',', ';', '\t', '|']:
                dialect = detected
        except:
            pass  # Use default 'excel'

        expected_totals = expected_totals or {}
        subjects = {}
        student_ids = set()  # Track unique student IDs

        reader = csv.DictReader(file_obj, dialect=dialect)
        for raw_row in reader:
            row = {self._normalize_key(k): v.strip() if isinstance(v, str) else v for k, v in raw_row.items()}

            # Extract student ID
            student_id_key = self._find_column_name(row, [
                'student_id', 'student', 'id', 'user_id', 'learner_id', 'enrollment_id'
            ])
            student_id = row.get(student_id_key, 'Unknown').strip() if student_id_key else 'Unknown'
            student_ids.add(student_id)

            subject_key = self._find_column_name(row, [
                'subject', 'course', 'course_name', 'class', 'category', 'module', 'topic'
            ])
            component_key = self._find_column_name(row, [
                'component', 'component_name', 'assessment', 'assessment_type', 'task', 'item', 'activity', 'section'
            ])
            score_key = self._find_column_name(row, [
                'score', 'marks', 'points', 'obtained', 'grade', 'points_earned'
            ])
            max_key = self._find_column_name(row, [
                'max_score', 'max_points', 'total_points', 'possible', 'out_of', 'max'
            ])
            weight_key = self._find_column_name(row, [
                'weight', 'weight_value', 'percentage_weight', 'weight_pct', 'weight_percentage'
            ])
            expected_key = self._find_column_name(row, [
                'expected_total', 'expectedscore', 'target_total', 'target', 'expected'
            ])

            subject = row.get(subject_key, 'General').strip() if subject_key else 'General'
            component = row.get(component_key, '').strip() if component_key else ''
            score = self._parse_float(row.get(score_key), None)
            max_points = self._parse_float(row.get(max_key), 0.0)
            weight = self._parse_float(row.get(weight_key), None)
            row_expected = self._parse_float(row.get(expected_key), None)

            if subject not in subjects:
                subjects[subject] = {
                    'subject': subject,
                    'studentIds': [],  # Track student IDs for this course
                    'components': [],
                    'totalScore': 0.0,
                    'totalMax': 0.0,
                    'weightedScore': 0.0,
                    'expectedTotal': expected_totals.get(subject, default_expected_total),
                    'rows': [],
                }

            subject_entry = subjects[subject]
            if student_id not in subject_entry['studentIds']:
                subject_entry['studentIds'].append(student_id)
            component_entry = {
                'name': component or f'component_{len(subject_entry["components"]) + 1}',
                'score': score,
                'maxPoints': max_points if max_points > 0 else None,
                'weight': weight if weight is not None else None,
            }
            subject_entry['components'].append(component_entry)
            if score is not None:
                subject_entry['totalScore'] += score
            if max_points > 0:
                subject_entry['totalMax'] += max_points
            if score is not None and weight is not None and max_points > 0:
                subject_entry['weightedScore'] += (score / max_points) * weight
            elif score is not None and weight is not None:
                subject_entry['weightedScore'] += score * weight
            subject_entry['rows'].append(row)

            if row_expected is not None and row_expected > 0:
                subject_entry['expectedTotal'] = row_expected

        output = {
            'sourceFile': getattr(file_obj, 'name', 'uploaded_csv'),
            'subjects': [],
            'summary': {
                'grandTotal': 0.0,
                'grandMax': 0.0,
                'overallPercentage': 0.0,
            },
        }

        grand_total = 0.0
        grand_max = 0.0

        for subject, entry in subjects.items():
            entry['percentage'] = (
                round((entry['totalScore'] / entry['totalMax']) * 100, 2)
                if entry['totalMax'] > 0 else 0.0
            )
            entry['meetsExpectation'] = entry['totalScore'] >= entry['expectedTotal']
            entry['weightedScore'] = round(entry['weightedScore'], 2)
            entry['totalScore'] = round(entry['totalScore'], 2)
            entry['totalMax'] = round(entry['totalMax'], 2)
            entry['expectedTotal'] = round(entry['expectedTotal'], 2)
            entry.pop('rows', None)

            output['subjects'].append(entry)
            grand_total += entry['totalScore']
            grand_max += entry['totalMax']

        output['summary']['grandTotal'] = round(grand_total, 2)
        output['summary']['grandMax'] = round(grand_max, 2)
        output['summary']['overallPercentage'] = (
            round((grand_total / grand_max) * 100, 2)
            if grand_max > 0 else 0.0
        )

        return output

    @staticmethod
    def _normalize_key(key: str) -> str:
        """
        Normalize column name for fuzzy matching
        Converts to lowercase, removes spaces, converts to underscores
        
        Example: "Student ID" -> "student_id"
        
        Args:
            key: Column name to normalize
            
        Returns:
            str: Normalized column name (lowercase with underscores)
        """
        return key.strip().lower().replace(' ', '_') if isinstance(key, str) else ''

    @staticmethod
    def _parse_float(value, default=0.0) -> float:
        """
        Safely parse a value to float
        Distinguishes between empty/None (returns default) and 0
        
        Args:
            value: Value to parse (can be str, float, None, or empty string)
            default: Default value to return for None/empty string
            
        Returns:
            float: Parsed value or default
            
        Example:
            _parse_float("85") -> 85.0
            _parse_float("") -> None (if default=None)
            _parse_float(None) -> None (if default=None)
        """
        if value is None or value == '':
            return default
        try:
            return float(str(value).strip())
        except ValueError:
            return default

    @staticmethod
    def _find_column_name(row: dict, candidates: List[str]):
        """
        Find column name using fuzzy matching
        Tries to match normalized column names from candidates
        
        Example:
            row has key "Student_ID", candidates ["student_id", "id"]
            Returns "Student_ID" (original key, not normalized)
        
        Args:
            row: Dict with column names as keys
            candidates: List of normalized names to match against
            
        Returns:
            str: Original column name if found, None otherwise
        """
        for key in row.keys():
            nk = DataManager._normalize_key(key)
            if nk in candidates:
                return key
        return None

    def import_subject_scores_from_csv(
        self,
        file_path: str,
        expected_totals: dict = None,
        default_expected_total: float = 100.0,
    ) -> dict:
        """
        Import a CSV file from disk path
        Wrapper around import_subject_scores_from_file for file path input
        
        Args:
            file_path: Path to CSV file on disk
            expected_totals: Dict mapping course names to expected scores
            default_expected_total: Default expectation score
            
        Returns:
            dict: Parsed data (see import_subject_scores_from_file for structure)
        """
        with open(file_path, mode='r', encoding='utf-8-sig') as file:
            return self.import_subject_scores_from_file(
                file,
                expected_totals,
                default_expected_total,
            )

    @staticmethod
    def export_to_json(data: List[dict], output_path: str):
        """
        Export parsed data to JSON file
        
        Args:
            data: Data to export
            output_path: Path where JSON file will be written
        """
        with open(output_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)
