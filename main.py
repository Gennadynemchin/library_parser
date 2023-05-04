from requests import HTTPError
from pathlib import Path
import requests
import os
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlsplit


def check_for_redirect(response):
    for r in response.history:
        if r.status_code != 200:
            raise HTTPError


def parse_book_page(html_content):
    soup = BeautifulSoup(html_content, 'lxml')
    title_author = soup.find('h1').text.split('::')
    cover = soup.find(class_='bookimage').find('img')['src']
    title = title_author[0].strip()
    author = title_author[1].strip()
    comments = soup.find_all(class_='texts')
    genres = soup.find_all('span', class_='d_book')
    all_comments = []
    all_genres = []
    for comment in comments:
        filtered_comment = comment.find(class_='black').text.strip()
        all_comments.append(filtered_comment)
    for genre in genres:
        filtered_genre = genre.text.strip()
        all_genres.append(filtered_genre)

    content = {
        "cover": cover,
        "title": title,
        "author": author,
        "comments": all_comments,
        "genres": all_genres
    }

    return content


base_url = 'https://tululu.org'
folder = 'books'
img_folder = 'images'
Path(folder).mkdir(exist_ok=True)
Path(img_folder).mkdir(exist_ok=True)

for book in range(1, 2):
    download_url = f'{base_url}/txt.php?id={book}'
    parse_url = f'{base_url}/b{book}'
    try:
        download_response = requests.get(download_url)
        download_response.raise_for_status()
        check_for_redirect(download_response)

        parse_response = requests.get(parse_url)
        parse_response.raise_for_status()
        parsed_page = parse_book_page(parse_response.content)

        cover_url = urljoin(base_url, parsed_page['cover'])

        output_filename = sanitize_filename(parsed_page['title'])
        filepath = os.path.join(folder, f'{output_filename}.txt')

        with open(filepath, 'wb') as file:
            file.write(download_response.content)

        cover_response = requests.get(cover_url)
        cover_response.raise_for_status()

        img_title = urlsplit(cover_url).path
        img_filename = os.path.basename(img_title)
        imgpath = os.path.join(img_folder, img_filename)

        with open(imgpath, 'wb') as img_file:
                    img_file.write(cover_response.content)

    except HTTPError:
        print(f'The book with ID {book} has not been downloaded. Passed')
        continue
