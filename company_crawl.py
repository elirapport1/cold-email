from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from collections import deque
from urllib.parse import urlparse
import os
import re


# Regex pattern to match a URL
HTTP_URL_PATTERN = r'^http[s]*://.+'

domain = "seamind.ai"  # <- put your domain to be crawled
full_url = "https://seamind.ai"  # <- put your domain to be crawled with https or http

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

# print(get_domain_hyperlinks(domain, full_url))



def crawl(url):
    # Parse the URL and get the domain
    local_domain = urlparse(url).netloc
    print("this is local_domain: "+local_domain)
    # print("hello")

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

        # Use Playwright to get the page content
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(current_url)
            html = page.content()
            soup = BeautifulSoup(html, 'html.parser')
            text = soup.get_text()
            # Normalize whitespace to ensure each word is separated by a single space
            text = re.sub(r'\s+', ' ', text).strip()
            all_company_text.append(text)
            # # Save text from the url to a <url>.txt file
            # with open('text/'+local_domain+'/'+current_url[8:].replace("/", "_") + ".txt", "w", encoding="UTF-8") as f:
            #     f.write(text)

            browser.close()

        # Get the hyperlinks from the URL and add them to the queue
        for link in get_domain_hyperlinks(local_domain, current_url):
            if link not in seen:
                queue.append(link)
                seen.add(link)
    
    concatenated_text = " ".join(all_company_text)
    # Save text from the url to a <url>.txt file
    with open('text/'+local_domain+ ".txt", "w", encoding="UTF-8") as f:
        f.write(concatenated_text)
crawl(full_url)

# Embedding Section

# def remove_newlines(serie):
#     serie = serie.str.replace('\n', ' ')
#     serie = serie.str.replace('\\n', ' ')
#     serie = serie.str.replace('  ', ' ')
#     serie = serie.str.replace('  ', ' ')
#     return serie


# import pandas as pd
# # Create a list to store the text files
# texts=[]

# # Get all the text files in the text directory
# for file in os.listdir("text/" + domain + "/"):

#     # Open the file and read the text
#     with open("text/" + domain + "/" + file, "r", encoding="UTF-8") as f:
#         text = f.read()

#         # Omit the first 11 lines and the last 4 lines, then replace -, _, and #update with spaces.
#         texts.append((file[11:-4].replace('-',' ').replace('_', ' ').replace('#update',''), text))

# # Create a dataframe from the list of texts
# df = pd.DataFrame(texts, columns = ['fname', 'text'])

# # Set the text column to be the raw text with the newlines removed
# df['text'] = df.fname + ". " + remove_newlines(df.text)
# df.to_csv('processed/scraped.csv')
# df.head()

# import tiktoken
# # Load the cl100k_base tokenizer which is designed to work with the ada-002 model
# tokenizer = tiktoken.get_encoding("cl100k_base")

# df = pd.read_csv('processed/scraped.csv', index_col=0)
# df.columns = ['title', 'text']

# # Tokenize the text and save the number of tokens to a new column
# df['n_tokens'] = df.text.apply(lambda x: len(tokenizer.encode(x)))

# # Visualize the distribution of the number of tokens per row using a histogram
# # df.n_tokens.hist()
# max_tokens = 500

# # Function to split the text into chunks of a maximum number of tokens
# def split_into_many(text, max_tokens = max_tokens):

#     # Split the text into sentences
#     sentences = text.split('. ')

#     # Get the number of tokens for each sentence
#     n_tokens = [len(tokenizer.encode(" " + sentence)) for sentence in sentences]

#     chunks = []
#     tokens_so_far = 0
#     chunk = []

#     # Loop through the sentences and tokens joined together in a tuple
#     for sentence, token in zip(sentences, n_tokens):

#         # If the number of tokens so far plus the number of tokens in the current sentence is greater
#         # than the max number of tokens, then add the chunk to the list of chunks and reset
#         # the chunk and tokens so far
#         if tokens_so_far + token > max_tokens:
#             chunks.append(". ".join(chunk) + ".")
#             chunk = []
#             tokens_so_far = 0

#         # If the number of tokens in the current sentence is greater than the max number of
#         # tokens, go to the next sentence
#         if token > max_tokens:
#             continue

#         # Otherwise, add the sentence to the chunk and add the number of tokens to the total
#         chunk.append(sentence)
#         tokens_so_far += token + 1

#     return chunks


# shortened = []

# # Loop through the dataframe
# for row in df.iterrows():

#     # If the text is None, go to the next row
#     if row[1]['text'] is None:
#         continue

#     # If the number of tokens is greater than the max number of tokens, split the text into chunks
#     if row[1]['n_tokens'] > max_tokens:
#         shortened += split_into_many(row[1]['text'])

#     # Otherwise, add the text to the list of shortened texts
#     else:
#         shortened.append( row[1]['text'] )

# df = pd.DataFrame(shortened, columns = ['text'])
# df['n_tokens'] = df.text.apply(lambda x: len(tokenizer.encode(x)))

# from openai import OpenAI
# from dotenv import load_dotenv

# load_dotenv()
# client = OpenAI()
# df['embeddings'] = df.text.apply(lambda x: client.embeddings.create(input=x, model='text-embedding-ada-002').data[0].embedding)
# df.to_csv('processed/embeddings.csv')
# df.head()


# import numpy as np
# from openai.embeddings_utils import distances_from_embeddings

# df=pd.read_csv('processed/embeddings.csv', index_col=0)
# df['embeddings'] = df['embeddings'].apply(eval).apply(np.array)

# df.head()