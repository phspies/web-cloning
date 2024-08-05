import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
from urllib.parse import urljoin, urlparse
import os
import time
import threading
from queue import Queue
import re
from slugify import slugify
from enum import Enum

class CrawlMode(Enum):
    DEFAULT = 1
    HOST_ONLY = 2
    SUBDOMAINS = 3

def get_domain(url):
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"

def sanitize_path(path):
    return slugify(path)

def crawl_page(start_url, url, output_folder, domain, visited_urls, urls_to_visit, mode, driver, include_pattern, exclude_pattern):
    if url in visited_urls:
        return

    try:
        driver.get(url)

        try:
            WebDriverWait(driver, 30).until(lambda driver: driver.execute_script("return document.readyState") == "complete")
        except TimeoutException as err:
            raise TimeoutError("Page not loaded") from err

        # Get the page source after JavaScript execution
        page_source = driver.page_source

        # Parse the page with BeautifulSoup
        soup = BeautifulSoup(page_source, 'html.parser')

        # Extract text content
        text_content = soup.get_text(separator='\n', strip=True)

        # Save text content to a file
        file_name = f"{sanitize_path(url)}.txt"
        file_path = os.path.join(output_folder, file_name)
        print(f"Crawled: {url} -> {file_path}")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text_content)

        # Find all links on the page
        links = soup.find_all('a', href=True)
        for link in links:
            absolute_url = urljoin(url, link['href'])
            if should_crawl(start_url, absolute_url, mode, include_pattern, exclude_pattern) and absolute_url not in visited_urls:
                urls_to_visit.put(absolute_url)

        visited_urls.add(url)

    except Exception as e:
        print(f"Error crawling {url}: {str(e)}")

def should_crawl(start_url, url, mode, include_pattern, exclude_pattern):
    start_parsed = urlparse(start_url)
    url_parsed = urlparse(url)
    
    # Check if the URL matches the include pattern (if provided)
    if include_pattern and not re.search(include_pattern, url):
        return False
    
    # Check if the URL matches the exclude pattern (if provided)
    if exclude_pattern and re.search(exclude_pattern, url):
        return False
    
    if mode == CrawlMode.DEFAULT:
        return url.startswith(start_url)
    elif mode == CrawlMode.HOST_ONLY:
        return start_parsed.netloc == url_parsed.netloc
    elif mode == CrawlMode.SUBDOMAINS:
        return start_parsed.netloc.split('.')[-2:] == url_parsed.netloc.split('.')[-2:]
    else:
        return False

def worker(start_url, output_folder, domain, visited_urls, urls_to_visit, mode, include_pattern, exclude_pattern):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        while True:
            url = urls_to_visit.get()
            if url is None:
                break
            crawl_page(start_url, url, output_folder, domain, visited_urls, urls_to_visit, mode, driver, include_pattern, exclude_pattern)
            urls_to_visit.task_done()
    finally:
        driver.quit()

def crawl_website(start_url, num_threads=5, mode=CrawlMode.DEFAULT, include_pattern=None, exclude_pattern=None):
    visited_urls = set()
    urls_to_visit = Queue()
    urls_to_visit.put(start_url)
    domain = get_domain(start_url)
    output_folder = sanitize_path(urlparse(start_url).hostname)
    print(f"Writing output to {output_folder}")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    threads = []
    for _ in range(num_threads):
        t = threading.Thread(target=worker, args=(start_url, output_folder, domain, visited_urls, urls_to_visit, mode, include_pattern, exclude_pattern))
        t.start()
        threads.append(t)

    urls_to_visit.join()

    for _ in range(num_threads):
        urls_to_visit.put(None)

    for t in threads:
        t.join()

# Example usage:
crawl_website(
    "https://rarediseases.info.nih.gov/diseases",
    mode=CrawlMode.DEFAULT,
    include_pattern=r"/diseases",  # Only crawl URLs containing "/diseases"
)
