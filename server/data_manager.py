# ==========================================
# Author: Pham Gia Bao (Student ID: AUS15065)
# Project ID: TEC004/05
# Description: SP2 - Multi-threaded File I/O & Processing
# ==========================================

import csv
import json
import threading
import time
from typing import List

def time_logger(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"[{func.__name__}] Executed in {time.time() - start:.4f} seconds")
        return result
    return wrapper

class DataManager:
    @staticmethod
    def process_csv_chunk(file_path: str, results_list: List):
        try:
            with open(file_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                cleaned_data = list(map(lambda row: {k: v.strip() for k, v in row.items()}, reader))
                results_list.extend(cleaned_data)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    @time_logger
    def batch_import_csv(self, file_paths: List[str]) -> List[dict]:
        threads = []
        combined_results = []
        
        for path in file_paths:
            thread = threading.Thread(target=self.process_csv_chunk, args=(path, combined_results))
            threads.append(thread)
            thread.start()
            
        for thread in threads:
            thread.join() 
            
        return combined_results

    @staticmethod
    def export_to_json(data: List[dict], output_path: str):
        with open(output_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)