from bs4 import BeautifulSoup


def parse_book_page(html_content):
    soup = BeautifulSoup(html_content, "lxml")
    author_title = soup.select_one("h1").text.split("::")
    author = author_title[1].strip()
    title = author_title[0].strip()
    cover_url = soup.select_one(".bookimage img")["src"]
    all_comments = [comment.text for comment in soup.select(".texts .black")]
    all_genres = [
        " ".join(genre.text.split()) for genre in soup.select("span.d_book a")
    ]
    content = {
        "cover": cover_url,
        "title": title,
        "author": author,
        "comments": all_comments,
        "genres": all_genres,
    }
    return content
