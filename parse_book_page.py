from bs4 import BeautifulSoup


def parse_book_page(html_content):
    soup = BeautifulSoup(html_content, "lxml")
    title_author = soup.find("h1").text.split("::")
    cover_url = soup.find(class_="bookimage").find("img")["src"]
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
        "cover": cover_url,
        "title": title,
        "author": author,
        "comments": all_comments,
        "genres": all_genres,
    }
    return content
