from collections import OrderedDict
from urllib.parse import urljoin
import logging
import requests
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
            log.info("The link %s has been saved", book_link)
    return download_urls
