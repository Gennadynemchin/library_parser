import argparse
import os
import requests
from requests import HTTPError
from pathlib import Path
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlsplit


def check_for_redirect(response):
    for r in response.history:
        if r.status_code != 200:
            raise HTTPError


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


def main():
    parser = argparse.ArgumentParser(description="Парсер книг с сайта tululu.org")
    parser.add_argument(
        "start_id", nargs="?", type=int, default=1, help="Start id for downloading"
    )
    parser.add_argument(
        "end_id", nargs="?", type=int, default=20, help="Last id for downloading"
    )
    args = parser.parse_args()

    BASE_URL = "https://tululu.org"
    BOOKS_FOLDER = "books"
    IMG_FOLDER = "images"
    Path(BOOKS_FOLDER).mkdir(exist_ok=True)
    Path(IMG_FOLDER).mkdir(exist_ok=True)

    for book in range(args.start_id, args.end_id+1):
        download_url = f"{BASE_URL}/txt.php?id={book}"
        parse_url = f"{BASE_URL}/b{book}"
        try:
            download_response = requests.get(download_url)
            download_response.raise_for_status()
            check_for_redirect(download_response)

            parse_response = requests.get(parse_url)
            parse_response.raise_for_status()
            parsed_page = parse_book_page(parse_response.content)

            output_filename = sanitize_filename(parsed_page["title"])
            filepath = os.path.join(BOOKS_FOLDER, f"{output_filename}.txt")

            with open(filepath, "wb") as file:
                file.write(download_response.content)

            cover_url = urljoin(BASE_URL, parsed_page["cover"])
            cover_response = requests.get(cover_url)
            cover_response.raise_for_status()

            img_title = urlsplit(cover_url).path
            img_filename = os.path.basename(img_title)
            imgpath = os.path.join(IMG_FOLDER, img_filename)

            with open(imgpath, "wb") as img_file:
                img_file.write(cover_response.content)
            print(
                f"Book {parsed_page.get('title')} has been downloaded\n"
                f"Genre: {parsed_page.get('genres')}\n"
                f"Comments: {parsed_page.get('comments')}\n\n"
            )
        except HTTPError:
            print(f"The book with ID {book} has not been downloaded. Passed")
            continue


if __name__ == "__main__":
    main()
