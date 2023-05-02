import requests
from pathlib import Path
from requests import HTTPError


BOOK_FOLDER = 'books'
Path(BOOK_FOLDER).mkdir(exist_ok=True)

def check_for_redirect(response):
    for r in response.history:
        if r.status_code != 200:
            raise HTTPError


for book in range(1, 11):
    url = f'https://tululu.org/txt.php?id={book}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        check_for_redirect(response)
        filename = f'{BOOK_FOLDER}/book_{book}.txt'
        with open(filename, 'wb') as file:
            file.write(response.content)
    except HTTPError:
        print(f'The book with ID {book} has not been downloaded. Passed')
        continue
