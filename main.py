import requests
from bs4 import BeautifulSoup, NavigableString, Tag
from openai import OpenAI
from dotenv import load_dotenv
from playwright.async_api import async_playwright
from directory_scrape import get_directory_links
import asyncio



def identify_companies_with_openai(text):
    load_dotenv()
    client = OpenAI()
    # openai.api_key = os.getenv('OPENAI_API_KEY')
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




# www.seedtable.com
# https://www.seedtable.com/startups-san-francisco
# https://growthlist.co/pre-seed-startups/
# https://growthlist.co/pre-seed-startups/

async def main():
    directory_url = "https://topstartups.io/?company_size=1-10+employees&company_size=11-50+employees"
    directory_links = await get_directory_links(directory_url)
    company_info = identify_companies_with_openai(directory_links)
    


# directory_html = asyncio.run(get_directory_links(url))

# print(company_info)

asyncio.run(main())