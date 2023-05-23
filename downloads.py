import os
import requests
from urllib.parse import urljoin, urlsplit


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def download_text(download_url, book_id, session):
    params = {"id": book_id}
    response_download = session.get(download_url, params=params)
    response_download.raise_for_status()
    check_for_redirect(response_download)
    return response_download.content


def download_cover(url, img_url, session):
    cover_url = urljoin(url, img_url)
    cover_response = session.get(cover_url)
    cover_response.raise_for_status()
    check_for_redirect(cover_response)
    img_title = urlsplit(cover_url).path
    img_filename = os.path.basename(img_title)
    content = {"filename": img_filename, "img": cover_response.content}
    return content
