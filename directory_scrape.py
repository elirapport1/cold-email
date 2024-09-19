from playwright.async_api import async_playwright
from collections import deque
import pprint
from urllib.parse import urlparse, urljoin
import re
from bs4 import BeautifulSoup
import asyncio
import os
from dotenv import load_dotenv
from openai import OpenAI

# Regex pattern to match a URL
HTTP_URL_PATTERN = r'^(https?://)?[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$'

async def get_directory_links(full_url):
    
    external_links = set()
    # Parse the full URL to extract the domain
    parsed_url = urlparse(full_url)
    domain = parsed_url.netloc
    print("domain: ", domain)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        try:
            await page.goto(full_url, timeout=100000)  # Set a timeout to avoid indefinite stalling
        except Exception as e:
            print(f"Failed to load {full_url}: {e}")  # Log any errors during page load
        html = await page.content()
        soup = BeautifulSoup(html, 'html.parser')
        await page.close()
        await browser.close()
        # Remove header and footer content
        for header in soup.find_all('header'):
            header.decompose()
        for footer in soup.find_all('footer'):
            footer.decompose()
        # return soup
        # Extract text content
        text_content = soup.get_text(separator=' ', strip=True)
        
        # Filter text_content to only include potential startup names or website URLs
        filtered_content = re.findall(r'\b(?:\w+\.){1,2}\w+\b', text_content)
        
        # Join the filtered content into a single string
        text_content = '\n'.join(filtered_content)

        # Extract links
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if re.match(HTTP_URL_PATTERN, href):
                links.append(href)
            elif href.startswith('/'):
                # Handle relative URLs
                links.append(urljoin(full_url, href))
        # print(links)
        # Remove links that contain the domain
        links = [link for link in links if not link.startswith(f"https://{domain}") and not link.startswith(f"http://{domain}")]
        # Combine links and text into one string
        combined_content = "Links:\n" + "\n".join(links) + "\n" + text_content
        # Create a file with combined content
        filename = f"directories/{domain}/links_raw.txt"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(combined_content)
        
        print(f"Combined content has been saved to '{filename}'")
        
        return combined_content



def identify_companies_with_openai(text):
    load_dotenv()
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a highly skilled assistant capable of identifying early stage startup companies' websites and names from a list of links scraped from a html page. Confirm each startup's standalone website by searching the web."},
            {"role": "user", "content": f"""Given a list of links scraped from a html page that lists startups, identify all startup company names and find the single link to their standalone website (independent of the directory's site). Search the web to confirm each startups' website. 
             Your response must be formatted as one startup per line with: 'startup name, startup website'. Here is the list of links: {text}"""}
        ]
    )
    response_content = response.choices[0].message.content.strip()
    
    # Parse the response content into a dictionary
    companies = {}
    for line in response_content.split('\n'):
        if ',' in line:
            company_name, website = line.split(',', 1)
            company_name = company_name.strip()
            website = website.strip()
            companies[company_name] = website
    print(companies)
    return companies

# directory_url = "https://topstartups.io/?company_size=1-10+employees&company_size=11-50+employees"
# directory_links = get_directory_links(directory_url)
# company_info = identify_companies_with_openai(directory_links)