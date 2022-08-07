from configparser import ConfigParser
import json
import os
from pathlib import Path
import sys

from bs4 import BeautifulSoup
import requests

from MyAnimeListPy import MyAnimeList
import MyAnimeListPy.utils
import anilist_query as al_query
import utils
from utils.download import download

# max number of pages to search
DEFAULT_PAGE_LIMIT = 5
# number of entries per page
ITEMS_PER_PAGE = 50

def run(base_path:Path, page_limit:int=DEFAULT_PAGE_LIMIT):
    if not isinstance(base_path, Path):
        base_path = Path(base_path).resolve()
    base_path.mkdir(exist_ok=True, parents=True)

    base_url = "https://myanimelist.net/anime.php?o=9&c%5B0%5D=a&c%5B1%5D=d&cv=2&w=1&show={}"

    mal_client = MyAnimeList(None)
    
    search_results = 0
    results_url = base_url

    # how many old entries to find before stopping
    limit = page_limit * ITEMS_PER_PAGE

    while True:

        # stop program if limit reached
        if limit <= 0:
            print("Threshold for old entries reached.\nQuitting program.")
            return

        results_url = base_url.format(search_results)

        # skip bad pages
        if not mal_client.validate_url(results_url): return

        req = download(results_url, mal_client.session, mal_client.rate_limit)    # the results page
        soup = BeautifulSoup(req.content, "html.parser")

        # Looping through each anime in the page
        for elem in soup.select("a[id^='sinfo']"):
            # print("------------------------")
            title = elem.select_one("strong").text
            MAL_id = MyAnimeListPy.utils.get_id(elem["href"])    # extract MAL id from url

            # Skip old entries
            if (base_path / f"{MAL_id}.json").exists():
                    print(f'Skipping {MAL_id:6} | <{title}>...')
                    limit -= 1 # decrement limit for every old entry discovered
                    continue

            # Get information from MAL and parse it
            print(f'Scrapping from MAL {MAL_id:6} | <{title}>...')
            MAL_metadata = mal_client.get_anime(MAL_id).gather_data()

            # Use MAL id to query AniList.co.
            print(f'Querying Anilist.co for <{title}>...')
            AL_metadata = al_query.query_idMal(MAL_id)

            # Combine MAL and AniList metadata (create function to do so).
            all_metadata = utils.combine_sources(MAL_metadata, AL_metadata)

            try:
                # Write the metadata to a json file, using the MAL id as the
                # filename.
                print(f"Dumping <{title}>...")
                with (base_path / f"{MAL_id}.json").open("w+", encoding="utf-8") as outfile:
                    outfile.write(json.dumps(all_metadata, indent=4, ensure_ascii=False))
                print("------------------------")
            except Exception as e:
                # Ensure incomplete files are deleted.
                print("Dumping interrupted. Deleting file.")
                if (base_path / f"{MAL_id}.json").exists():
                    os.remove((base_path / f"{MAL_id}.json"))
                raise e
    
        # Look for the next 50 results
        search_results += 50
        print("------------------------")


if __name__ == '__main__':
    config = ConfigParser()
    if not os.path.exists("config.ini"):
        config.read("example.config.ini")
    else:        
        config.read("config.ini")
    
    path = config["DB"]["Path"]

    if len(sys.argv) > 1:
        run(path, page_limit=int(sys.argv[1]))
    else:
        run(path)