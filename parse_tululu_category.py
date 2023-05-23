import argparse
import os
import requests
from time import sleep
from requests.adapters import HTTPAdapter, Retry
from urllib3.exceptions import NewConnectionError, MaxRetryError
from urllib.parse import urljoin, urlsplit
from pathlib import Path
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from tqdm import trange
from tqdm.contrib.logging import logging_redirect_tqdm



def pagination(url, page_limit, session):
    download_urls = []
    for page in range(page_limit):
        pagination_link = f'{url}/{page}'
        page_content = session.get(pagination_link)
        soup = BeautifulSoup(page_content.content, "lxml")
        ids = soup.find_all(class_="d_book")
        for id in ids:
            download_path = id.find(class_="bookimage").find("a")["href"]
            download_url = urljoin(url, download_path)
            download_urls.append(download_url)
    return download_urls


def main():
    total_retries = 3
    backoff_factor = 3

    session = requests.Session()
    retries = Retry(total=total_retries, backoff_factor=backoff_factor)
    session.mount("https://", HTTPAdapter(max_retries=retries))

    base_url = "https://tululu.org"
    science_fiction = "l55"
    science_fantazy_url = urljoin(base_url, science_fiction)
    page_limit = 200

    print(pagination(science_fantazy_url, page_limit, session))


if __name__ == "__main__":
    main()
