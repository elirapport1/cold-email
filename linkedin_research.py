from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def setup_driver():
    options = Options()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--disable-gpu")  # Disable GPU acceleration
    options.add_argument("--no-sandbox")  # Bypass OS security model
    options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)
    return driver

def search_jobs(driver, job_description):
    driver.get("https://www.linkedin.com/jobs/")
    # Wait for the search box to be present
    search_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[contains(@class, 'jobs-search-box__text-input')]"))
    )
    search_box.send_keys(job_description)
    search_box.send_keys(Keys.RETURN)
    time.sleep(5)

def scrape_job_results(driver):
    jobs = driver.find_elements(By.XPATH, "//a[contains(@class, 'result-card__full-card-link')]")
    job_list = []
    for job in jobs:
        job_list.append({
            'title': job.text,
            'link': job.get_attribute("href")
        })
    return job_list

def main():
    job_description = 'Software Engineer intern'  # Update with your job description

    driver = setup_driver()
    try:
        search_jobs(driver, job_description)
        job_results = scrape_job_results(driver)
        for job in job_results:
            print(f"Title: {job['title']}, Link: {job['link']}")
    finally:
        driver.quit()

main()