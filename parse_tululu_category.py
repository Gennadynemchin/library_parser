import logging
from collections import OrderedDict
from time import sleep
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from tqdm import trange
from urllib3.exceptions import MaxRetryError
from urllib3.exceptions import NewConnectionError

from downloads import check_for_redirect

log = logging.getLogger(__name__)


def get_book_pages(url, start_page, end_page, session):
    book_page_urls = []
    for page in trange(start_page, end_page, desc="Getting book links in progress", leave=True):
        pagination_link = f'{url}/{page}'
        page_content = session.get(pagination_link)
        page_content.raise_for_status()
        try:
            check_for_redirect(page_content)
        except requests.HTTPError:
            log.warning("Redirect detected")
            break
        except (
                MaxRetryError,
                NewConnectionError,
                requests.exceptions.Timeout,
                requests.exceptions.ConnectionError,
        ):
            log.warning("Try to reconnect soon")
            sleep(30)
        soup = BeautifulSoup(page_content.content, "lxml")
        page_links = [link["href"] for link in soup.select(".d_book a[href^='/b']")]
        book_ids = list(OrderedDict.fromkeys(page_links))
        for book_id in book_ids:
            book_link = urljoin(url, book_id)
            book_page_urls.append(book_link)
            log.info("The link %s has been saved", book_link)
    return book_page_urls


def get_max_page(url, session):
    page_content = session.get(f"{url}/1")
    page_content.raise_for_status()
    check_for_redirect(page_content)
    soup = BeautifulSoup(page_content.content, "lxml")
    max_page_number = [page.text for page in soup.select(".center .npage")][-1]
    return max_page_number
