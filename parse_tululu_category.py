from collections import OrderedDict
import requests
import logging
from requests.adapters import HTTPAdapter, Retry
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from tqdm import trange
from downloads import check_for_redirect


log = logging.getLogger(__name__)


def pagination(url, start_page, end_page, session):
    download_urls = []
    for page in trange(start_page, end_page, desc="Getting book links in progress", leave=True):
        pagination_link = f'{url}/{page}'
        page_content = session.get(pagination_link)
        try:
            check_for_redirect(page_content)
        except requests.HTTPError:
            break
        soup = BeautifulSoup(page_content.content, "lxml")
        page_links = [link["href"] for link in soup.select(".d_book a[href^='/b']")]
        book_ids = list(OrderedDict.fromkeys(page_links))
        for book_id in book_ids:
            book_link = urljoin(url, book_id)
            download_urls.append(book_link)
            log.info(f"The link {book_link} has been saved")
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
