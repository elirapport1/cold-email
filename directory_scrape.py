from playwright.async_api import async_playwright
from collections import deque
import pprint
from urllib.parse import urlparse, urljoin
import re
from bs4 import BeautifulSoup
import asyncio
import os




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



