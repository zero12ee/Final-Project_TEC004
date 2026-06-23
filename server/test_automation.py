# ==========================================
# Author: Nguyen Luong Nhat (Student ID: AUS14988)
# Project ID: TEC004/05
# Description: SP7 - Selenium Web Automation Test
# ==========================================

from selenium import webdriver
import time

def run_automated_test():
    print("Starting Selenium Web Automation Test...")
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)
    
    try:
        target_url = "http://localhost:5173" 
        driver.get(target_url)
        print(f"Navigated to {target_url}")
        time.sleep(3)
        print("Selenium test execution completed.")
    except Exception as e:
        print(f"Selenium test failed: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    run_automated_test()
