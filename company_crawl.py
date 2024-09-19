from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from collections import deque
from urllib.parse import urlparse
import os
import re
from googlesearch import search
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from webdriver_manager.chrome import ChromeDriverManager

# Regex pattern to match a URL
HTTP_URL_PATTERN = r'^http[s]*://.+'



# Function to get the hyperlinks from a URL using Playwright
def get_hyperlinks_playwright(url):
    hyperlinks = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        html = page.content()
        soup = BeautifulSoup(html, 'html.parser')
        hyperlinks = [link.get('href') for link in soup.find_all('a', href=True)]
        browser.close()
    return hyperlinks

# Function to get the hyperlinks from a URL that are within the same domain
def get_domain_hyperlinks(local_domain, url):
    clean_links = []
    for link in set(get_hyperlinks_playwright(url)):
        # print(link)
        clean_link = None

        # If the link is a URL, check if it is within the same domain
        if re.search(HTTP_URL_PATTERN, link):
            # Parse the URL and check if the domain is the same
            url_obj = urlparse(link)
            if url_obj.netloc == local_domain:
                clean_link = link

        # If the link is not a URL, check if it is a relative link
        else:
            if link.startswith("./"):
                link = link[2:]
            elif link.startswith("#") or link.startswith("mailto:"):
                continue
            clean_link = "https://" + local_domain + "/" + link
        if clean_link is not None:
            if clean_link.endswith("/"):
                clean_link = clean_link[:-1]
            clean_links.append(clean_link)
    # Return the list of hyperlinks that are within the same domain
    return list(set(clean_links))


def crawl(url):
    # Parse the URL and get the domain
    local_domain = urlparse(url).netloc
    print("this is local_domain: "+local_domain)

    # Create a queue to store the URLs to crawl
    queue = deque([url])

    # Create a set to store the URLs that have already been seen (no duplicates)
    seen = set([url])

    # Create a directory to store the text files
    if not os.path.exists("text/"):
        os.mkdir("text/")

    if not os.path.exists("text/"+local_domain+"/"):
        os.mkdir("text/" + local_domain + "/")

    all_company_text = []
    # While the queue is not empty, continue crawling
    while queue:
        # Get the next URL from the queue
        current_url = queue.pop()
        # print(current_url)  # for debugging and to see the progress
        all_company_text.append(get_page_text(current_url))

        # Get the hyperlinks from the URL and add them to the queue
        for link in get_domain_hyperlinks(local_domain, current_url):
            if link not in seen:
                queue.append(link)
                seen.add(link)
    
    concatenated_text = " ".join(all_company_text)
    return concatenated_text

# Use Playwright to get the page content
def get_page_text(url):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        html = page.content()
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text()
        # Normalize whitespace to ensure each word is separated by a single space
        text = re.sub(r'\s+', ' ', text).strip()
        # Add a header for the text on the current page
        page_header = f"Header: {url}\n"
        browser.close()
        return page_header + text + "\n"


def get_top_google_results(company_name, num_results=4):

    query = company_name
    top_results = []

    try:
        # Perform a Google search and get the top 3 results
        for result in search(query, num_results):
            top_results.append(result)
            get_page_text(result)
    except Exception as e:
        print(f"An error occurred while searching for {company_name}: {e}")

    return top_results


# print(get_top_google_results("claim.co startup company"))


def initialize_company(company_name):
    company = {
        "company_name": company_name,
        "website_text": [],
        "webpage_discussions": [],
        "employees": [],
        "first_contact": {
            "message": "",
            "date_sent": "",
            "outlook_link": "",
            "linkedin_link": ""
        },
        "second_contact": {
            "message": "",
            "date_sent": "",
            "outlook_link": "",
            "linkedin_link": ""
        },
        "third_contact": {
            "message": "",
            "date_sent": "",
            "outlook_link": "",
            "linkedin_link": ""
        },
        "linkedin_scraped_text": "",
        "processed_info": {
            "latest_news": "",
            "office_locations": "",
            "tech_stack": [],
            "company_pain_points": "",
            "contacts_history": [],
            "target_research": ""
        }
    }
    return company

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def scrape_linkedin_company_page(company_name):
    driver = setup_driver()
    linkedin_url = f"https://www.linkedin.com/company/{company_name}/"
    driver.get(linkedin_url)
    
    company_info = {}
    
    try:
        # Wait for the company name to be present
        company_name_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h1[contains(@class, 'org-top-card-summary__title')]"))
        )
        company_info['name'] = company_name_element.text
        
        # Scrape company description
        description_element = driver.find_element(By.XPATH, "//p[contains(@class, 'org-top-card-summary__tagline')]")
        company_info['description'] = description_element.text
        
        # Scrape number of employees
        employees_element = driver.find_element(By.XPATH, "//span[contains(@class, 'org-top-card-summary-info-list__info-item')]")
        company_info['employees'] = employees_element.text
        
        # Scrape company website
        website_element = driver.find_element(By.XPATH, "//a[contains(@class, 'org-about-company-module__website')]")
        company_info['website'] = website_element.get_attribute("href")
        
    except Exception as e:
        print(f"An error occurred while scraping LinkedIn page for {company_name}: {e}")
    finally:
        driver.quit()
    
    return company_info


def main():
    domain = "claim.co"
    full_url = "https://www.claim.co/"
    claim = initialize_company("claim")

    



if __name__ == "__main__":
    main()
