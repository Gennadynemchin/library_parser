import argparse
import os
import logging
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



log = logging.getLogger(__name__)


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def parse_book_page(html_content):
    soup = BeautifulSoup(html_content, "lxml")
    title_author = soup.find("h1").text.split("::")
    cover = soup.find(class_="bookimage").find("img")["src"]
    title = title_author[0].strip()
    author = title_author[1].strip()
    comments = soup.find_all(class_="texts")
    genres = soup.find_all("span", class_="d_book")
    all_comments = []
    all_genres = []
    for comment in comments:
        filtered_comment = comment.find(class_="black").text
        all_comments.append(" ".join(filtered_comment.split()))
    for genre in genres:
        all_genres.append(" ".join(genre.text.split()))
    content = {
        "cover": cover,
        "title": title,
        "author": author,
        "comments": all_comments,
        "genres": all_genres,
    }
    return content


def download_text(download_url, book_id, session, retries):
    params = {'id': book_id}
    response_download = session.get(download_url, params=params)
    response_download.raise_for_status()
    check_for_redirect(response_download)
    return response_download.content


def download_cover(url, img_url, session, retries):
    cover_url = urljoin(url, img_url)
    cover_response = session.get(cover_url)
    cover_response.raise_for_status()
    check_for_redirect(cover_response)
    img_title = urlsplit(cover_url).path
    img_filename = os.path.basename(img_title)
    content = {"filename": img_filename,
               "img": cover_response.content
               }
    return content


def main():
    parser = argparse.ArgumentParser(description="Парсер книг с сайта tululu.org")
    parser.add_argument("start_id", nargs="?", type=int, default=1, help="Start id for downloading")
    parser.add_argument("end_id", nargs="?", type=int, default=100, help="Last id for downloading")
    args = parser.parse_args()

    base_url = "https://tululu.org"
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
        session.mount('https://', HTTPAdapter(max_retries=retries))

        for book_id in trange(args.start_id, args.end_id + 1, desc='Task in progress', leave=True):
            download_url = f"{base_url}/txt.php"
            parse_url = f"{base_url}/b{book_id}/"
            try:
                response_download = download_text(download_url, book_id, session, retries)

                response_parse = session.get(parse_url)
                check_for_redirect(response_parse)

                parsed_page = parse_book_page(response_parse.content)
                cover_response = download_cover(parse_url, parsed_page["cover"], session, retries)

            except requests.HTTPError:
                log.info(f"The book with ID {book_id} has been passed")
                continue
            except (
                    MaxRetryError,
                    NewConnectionError,
                    requests.exceptions.Timeout,
                    requests.exceptions.ConnectionError
                    ):
                log.info(f"Try to reconnect soon. The book with ID {book_id} passed")
                sleep(30)

            else:
                output_filename = sanitize_filename(parsed_page["title"])
                filepath = os.path.join(books_folder, f"{output_filename}.txt")
                imgpath = os.path.join(img_folder, cover_response['filename'])

                with open(filepath, "wb") as file:
                    file.write(response_download)
                with open(imgpath, "wb") as img_file:
                    img_file.write(cover_response['img'])
                log.info(f"Book {parsed_page.get('title')} with ID {book_id} has been downloaded")


if __name__ == "__main__":
    main()

