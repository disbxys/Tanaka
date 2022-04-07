from bs4 import BeautifulSoup
import requests

from MyAnimeListPy.utils.download import download

PER_PAGE = 50

def main() -> None:
    results = get_search_results(page_num=0*PER_PAGE)
    for result in results:
        print(result)


def scrap_all(base_path) -> None:
    search_constants = (
        ".", "A", "B", "C", "D", "E", "F", "G", "H", "I",
        "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S",
        "T", "U", "V", "W", "X", "Y", "Z"
    )
    pass


def get_search_results(letter:str=".", page_num:int=0) -> list:
    base_search_url = "https://myanimelist.net/anime.php?letter={}&show={}"
    return scrape_webpage(base_search_url.format(letter, page_num*50))


def get_updates(page_num:int=0) -> list:
    base_search_url = "https://myanimelist.net/anime.php?o=9&c%5B0%5D=a&c%5B1%5D=d&cv=2&w=1&show={}"
    return scrape_webpage(base_search_url.format(page_num))


def scrape_webpage(url:str) -> list:
    req = download(url)
    soup = BeautifulSoup(req.content, "html.parser")

    # Capture all html elements containing urls with a
    # myanimelist id.
    urls = list()
    for elem in soup.select("a[id^='sinfo']"):
        if elem: urls.append(elem["href"])

    return urls


if __name__ == '__main__':
    main()