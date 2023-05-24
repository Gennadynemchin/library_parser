from collections import OrderedDict
import requests
from requests.adapters import HTTPAdapter, Retry
from urllib.parse import urljoin
from bs4 import BeautifulSoup


def pagination(url, page_limit, session):
    download_urls = []
    for page in range(page_limit):
        pagination_link = f'{url}/{page}'
        page_content = session.get(pagination_link)
        soup = BeautifulSoup(page_content.content, "lxml")
        page_links = [link["href"] for link in soup.select(".d_book a[href^='/b']")]
        book_ids = list(OrderedDict.fromkeys(page_links))
        for book_id in book_ids:
            download_urls.append(urljoin(url, book_id))
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
    page_limit = 2
    pagination(science_fantazy_url, page_limit, session)


if __name__ == "__main__":
    main()
