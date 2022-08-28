from configparser import ConfigParser
import json
import os
from pathlib import Path
import sys

from bs4 import BeautifulSoup
from jikanpy import Jikan
from jikanpy.exceptions import APIException
from requests_ratelimiter import Duration, RequestRate, Limiter, LimiterSession

import utils

DEFAULT_PAGE_LIMIT = 5  # max number of pages to search
ITEMS_PER_PAGE = 50     # number of entries per page

def run(base_path:Path, page_limit:int=DEFAULT_PAGE_LIMIT):
    if not isinstance(base_path, Path):
        base_path = Path(base_path).resolve()
    base_path.mkdir(exist_ok=True, parents=True)

    base_url = "https://myanimelist.net/anime.php?o=9&c%5B0%5D=a&c%5B1%5D=d&cv=2&w=1&show={}"

    # set rate limit for jikanpy
    mal_rate = RequestRate(1, Duration.SECOND * 4)
    limiter = Limiter(mal_rate)

    session = LimiterSession(limiter=limiter)
    jikan = Jikan(selected_base="https://api.jikan.moe/v4", session=session)
    
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
        if not utils.validate_url(results_url): return

        req = session.get(results_url)    # the results page
        soup = BeautifulSoup(req.content, "html.parser")

        # Looping through each anime in the page
        for elem in soup.select("a[id^='sinfo']"):
            # print("------------------------")
            title = elem.select_one("strong").text
            MAL_id = utils.get_id(elem["href"])    # extract MAL id from url

            # Skip old entries
            if (base_path / f"{MAL_id}.json").exists():
                limit -= 1 # decrement limit for every old entry discovered
                continue

            try:
                # Get information from MAL and parse it
                MAL_metadata = jikan.anime(MAL_id)
            except APIException as e:
                if e.status_code == 408:
                    # If a timeout occurs, try one more
                    # time before raising the exception.
                    MAL_metadata = jikan.anime(MAL_id)
                    MAL_metadata = utils.filter_metadata(MAL_metadata)
                else:
                    raise e

            try:
                # Write the metadata to a json file, using the MAL id as the
                # filename.
                with (base_path / f"{MAL_id}.json").open("w+", encoding="utf-8") as outfile:
                    outfile.write(json.dumps(MAL_metadata, indent=4, ensure_ascii=False))
                print(f'Scrapped {MAL_id:6} | <{title}>...')
            except Exception as e:
                # Ensure incomplete files are deleted.
                print("Dumping interrupted. Deleting file.")
                if (base_path / f"{MAL_id}.json").exists():
                    os.remove((base_path / f"{MAL_id}.json"))
                raise e
            # return
    
        # Look for the next 50 results
        search_results += 50


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