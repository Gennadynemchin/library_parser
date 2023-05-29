import json
import logging
import os
from time import sleep
from urllib.parse import urljoin

import requests
from pathvalidate import sanitize_filename
from requests.adapters import HTTPAdapter
from requests.adapters import Retry
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm
from urllib3.exceptions import MaxRetryError
from urllib3.exceptions import NewConnectionError

from arg_parser import get_arg_parser
from downloads import check_for_redirect
from downloads import download_cover
from downloads import download_text
from parse_book_page import parse_book_page
from parse_tululu_category import get_book_pages
from parse_tululu_category import get_max_page

log = logging.getLogger(__name__)


def main():
    total_retries = 3
    backoff_factor = 3
    session = requests.Session()
    retries = Retry(total=total_retries, backoff_factor=backoff_factor)
    session.mount("https://", HTTPAdapter(max_retries=retries))
    base_url = "https://tululu.org"
    science_fiction = "l55"
    science_fantazy_url = urljoin(base_url, science_fiction)
    max_page = get_max_page(science_fantazy_url, session)
    args = get_arg_parser(max_page)
    start_page = args.start_page
    end_page = args.end_page
    books_folder = os.path.join(args.dest_folder, "books")
    img_folder = os.path.join(args.dest_folder, "images")
    os.makedirs(books_folder, exist_ok=True)
    os.makedirs(img_folder, exist_ok=True)
    os.makedirs(args.json_path, exist_ok=True)
    json_path = os.path.join(args.json_path, "books_info.json")

    logging.basicConfig(level=logging.INFO)

    with logging_redirect_tqdm():
        book_links = get_book_pages(science_fantazy_url, start_page, end_page, session)
        books_info = []
        for book_page_url in tqdm(
            book_links, desc="Getting book in progress", leave=True
        ):
            book_text_url = f"{base_url}/txt.php"
            book_id = int("".join(filter(str.isdigit, str(book_page_url))))
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
                log.warning("The book with ID %s has been passed", book_id)
                continue
            except (
                MaxRetryError,
                NewConnectionError,
                requests.exceptions.Timeout,
                requests.exceptions.ConnectionError,
            ):
                log.warning(
                    "Try to reconnect soon. The book with ID %s passed", book_id
                )
                sleep(30)
            else:
                if not args.skip_imgs:
                    imgpath = os.path.join(str(img_folder), cover_response["filename"])
                    with open(imgpath, "wb") as img_file:
                        img_file.write(cover_response["img"])
                else:
                    imgpath = None
                if not args.skip_txt:
                    output_filename = sanitize_filename(page_content["title"])
                    filepath = os.path.join(str(books_folder), f"{output_filename}.txt")
                    with open(filepath, "wb") as file:
                        file.write(book_content)
                else:
                    filepath = None
                log.info(
                    "Book %s with ID %s has been downloaded",
                    page_content.get("title"),
                    book_id,
                )
                content = {
                    "title": page_content.get("title"),
                    "author": page_content.get("author"),
                    "img_src": imgpath,
                    "book_path": filepath,
                    "comments": page_content.get("comments"),
                    "genres": page_content.get("genres"),
                }
                books_info.append(content)
        with open(json_path, "w") as books_data:
            json.dump(
                {"books_info": books_info}, books_data, indent=2, ensure_ascii=False
            )


if __name__ == "__main__":
    main()
