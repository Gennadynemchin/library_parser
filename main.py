from requests import HTTPError
from pathlib import Path
import requests
import os
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin


def check_for_redirect(response):
    for r in response.history:
        if r.status_code != 200:
            raise HTTPError


folder = 'books'
Path(folder).mkdir(exist_ok=True)

for book in range(13, 14):
    download_url = f'https://tululu.org/txt.php?id={book}'
    title_author_url = f'https://tululu.org/b{book}'
    try:
        download_response = requests.get(download_url)
        download_response.raise_for_status()
        check_for_redirect(download_response)
        title_author_response = requests.get(title_author_url)
        title_author_response.raise_for_status()

        soup = BeautifulSoup(title_author_response.text, 'lxml')
        title_author = soup.find('h1').text.split('::')
        cover = soup.find(class_='bookimage').find('img')['src']
        print(cover)
        cover_url = urljoin('https://tululu.org', cover)
        print(cover_url)
        title = title_author[0].strip()
        author = title_author[1].strip()
        output_filename = sanitize_filename(title)
        filepath = os.path.join(folder, f'{output_filename}.txt')

        with open(filepath, 'wb') as file:
            file.write(download_response.content)

    except HTTPError:
        print(f'The book with ID {book} has not been downloaded. Passed')
        continue




'''
soup = BeautifulSoup(response.text, 'lxml')
title_tag = soup.find('main').find('header').find('h1')
print(title_tag.text)
title_img = soup.find('img', class_='attachment-post-image')
print(title_img['src'])
page_text = soup.find(class_='entry-content').findAll('p')
print(page_text)
'''