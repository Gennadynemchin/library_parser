import argparse
import os
import json
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
    parser = argparse.ArgumentParser(description="Book parser tululu.org")
    parser.add_argument('--start_page', type=int, required=True, help='Start page for download')
    parser.add_argument('--end_page', type=int, required=False, help='Last page for download')
    args = parser.parse_args()

    base_url = "https://tululu.org"
    science_fiction = "l55"
    science_fantazy_url = urljoin(base_url, science_fiction)
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
        book_links = pagination(science_fantazy_url, args.start_page, args.end_page, session)
        items = []
        for book_page_url in tqdm(book_links, desc="Getting book in progress", leave=True):
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

                content = {"title": page_content.get('title'),
                           "author": page_content.get('author'),
                           "img_src": imgpath,
                           "book_path": filepath,
                           "comments": page_content.get('comments'),
                           "genres": page_content.get('genres')}
                items.append(content)

        books_info = json.dumps({"items": items}, indent=2, ensure_ascii=False)
        with open("books_info.json", "w") as my_file:
            my_file.write(books_info)


if __name__ == "__main__":
    main()
