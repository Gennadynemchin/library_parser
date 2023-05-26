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

'''
def dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)
'''

def main():
    parser = argparse.ArgumentParser(description="Book parser tululu.org")
    parser.add_argument('--start_page', type=int, required=True, help='Start page for download')
    parser.add_argument('--end_page', type=int, required=False, help='Last page for download')
    parser.add_argument('--dest_folder', type=str, default='media')
    parser.add_argument('--json_path', type=str, default='json')
    parser.add_argument('--skip_imgs', action='store_true')
    parser.add_argument('--skip_txt', action='store_true')
    args = parser.parse_args()

    base_url = "https://tululu.org"
    science_fiction = "l55"
    science_fantazy_url = urljoin(base_url, science_fiction)

    books_folder = os.path.join(args.dest_folder, "books")
    img_folder = os.path.join(args.dest_folder, "images")

    os.makedirs(books_folder, exist_ok=True)
    os.makedirs(img_folder, exist_ok=True)
    os.makedirs(args.json_path, exist_ok=True)
    json_path = os.path.join(args.json_path, "books_info.json")
    if args.skip_imgs:
        print('Skipped')
    else:
        print('Not skipped')
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
        with open(json_path, "w") as my_file:
            my_file.write(books_info)


if __name__ == "__main__":
    main()
