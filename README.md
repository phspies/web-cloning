# Web Crawler

This is a multi-threaded web crawler implemented in Python. It uses Selenium WebDriver for JavaScript rendering and BeautifulSoup for HTML parsing.

## Features

- Multi-threaded crawling for improved performance
- JavaScript rendering support using Selenium
- Flexible crawling modes (DEFAULT, HOST_ONLY, SUBDOMAINS)
- Include and exclude patterns for URL filtering
- Saves crawled content as text files
- Cleans folder from old content not discovered in the crawl

## Requirements

- Python 3.6+
- requests
- beautifulsoup4
- selenium
- python-slugify
  
```
pip install requests beautifulsoup4 selenium python-slugify
```

## Usage

```
crawl_website(
    "https://rarediseases.info.nih.gov/diseases",
    num_threads=5,
    mode=CrawlMode.DEFAULT,
    location=".",
    include_pattern = r"/diseases",  # Only crawl URLs containing "/diseases",
    exclude_pattern=r"(\.pdf|\.jpg|\.png)$"  # Exclude URLs ending with .pdf, .jpg, or .png
)
```
## Crawl Modes Available

CrawlMode.DEFAULT, CrawlMode.HOST_ONLY, CrawlMode.SUBDOMAINS
    
- Default: Limit crawling to web pages that belong to the same host and with the same initial URL path. For example, with a seed URL of "https://aws.amazon.com/bedrock/" then only this path and web pages that extend from this path will be crawled, like "https://aws.amazon.com/bedrock/agents/". Sibling URLs like "https://aws.amazon.com/ec2/" are not crawled, for example.
- Host only: Limit crawling to web pages that belong to the same host. For example, with a seed URL of "https://aws.amazon.com/bedrock/", then web pages with "https://docs.aws.amazon.com" will also be crawled, like "https://aws.amazon.com/ec2".
- Subdomains: Include crawling of any web page that has the same primary domain as the seed URL. For example, with a seed URL of "https://aws.amazon.com/bedrock/" then any web page that contains "amazon.com" will be crawled, like "https://www.amazon.com".
