import requests
from bs4 import BeautifulSoup


url = 'https://tululu.org/b1'
response = requests.get(url)
response.raise_for_status()

soup = BeautifulSoup(response.text, 'lxml')
title_author = soup.find('h1').text.split('::')
title = title_author[0].strip()
author = title_author[1].strip()
print(title, author)


def download_txt(url, filename, folder):
    pass



'''
soup = BeautifulSoup(response.text, 'lxml')
title_tag = soup.find('main').find('header').find('h1')
print(title_tag.text)
title_img = soup.find('img', class_='attachment-post-image')
print(title_img['src'])
page_text = soup.find(class_='entry-content').findAll('p')
print(page_text)
'''