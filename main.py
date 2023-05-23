import argparse
import os
import logging
import requests
from time import sleep
from requests.adapters import HTTPAdapter, Retry
from urllib3.exceptions import NewConnectionError, MaxRetryError
from urllib.parse import urljoin, urlsplit
from pathlib import Path
from pathvalidate import sanitize_filename
from tqdm import tqdm, trange
from tqdm.contrib.logging import logging_redirect_tqdm
from parse_tululu_category import pagination
from parse_book_page import parse_book_page
from downloads import download_text, download_cover, check_for_redirect


log = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Парсер книг с сайта tululu.org")
    parser.add_argument(
        "start_id", nargs="?", type=int, default=1, help="Start id for downloading"
    )
    parser.add_argument(
        "end_id", nargs="?", type=int, default=5, help="Last id for downloading"
    )
    args = parser.parse_args()

    base_url = "https://tululu.org"
    science_fiction = "l55"
    science_fantazy_url = urljoin(base_url, science_fiction)
    page_limit = 10
    books_folder = "books"
    img_folder = "images"
    Path(books_folder).mkdir(exist_ok=True)
    Path(img_folder).mkdir(exist_ok=True)
    logging.basicConfig(level=logging.INFO)

    with logging_redirect_tqdm():
        total_retries = 3
        backoff_factor = 3

        session = requests.Session()
        retries = Retry(total=total_retries, backoff_factor=backoff_factor)
        session.mount("https://", HTTPAdapter(max_retries=retries))
        book_links = pagination(science_fantazy_url, page_limit, session)

        for book_page_url in tqdm(book_links, desc="Getting book links in progress", leave=True):


        # for book_id in trange(args.start_id, args.end_id + 1, desc="Task in progress", leave=True):

            book_text_url = f"{base_url}/txt.php"
            # book_page_url = f"{base_url}/b{book_id}/"
            book_id = int(''.join(filter(str.isdigit, str(book_page_url))))
            try:
                book_content = download_text(book_text_url, book_id, session)

                book_page = session.get(book_page_url)
                book_page.raise_for_status()
                check_for_redirect(book_page)

                page_content = parse_book_page(book_page.content)
                cover_response = download_cover(
                    book_page_url, page_content["cover"], session
                )

            except requests.HTTPError:
                log.info(f"The book with ID {book_id} has been passed")
                continue
            except (
                MaxRetryError,
                NewConnectionError,
                requests.exceptions.Timeout,
                requests.exceptions.ConnectionError,
            ):
                log.info(f"Try to reconnect soon. The book with ID {book_id} passed")
                sleep(30)

            else:
                output_filename = sanitize_filename(page_content["title"])
                filepath = os.path.join(books_folder, f"{output_filename}.txt")
                imgpath = os.path.join(img_folder, cover_response["filename"])

                with open(filepath, "wb") as file:
                    file.write(book_content)
                with open(imgpath, "wb") as img_file:
                    img_file.write(cover_response["img"])
                log.info(
                    f"Book {page_content.get('title')} with ID {book_id} has been downloaded"
                )


if __name__ == "__main__":
    main()
