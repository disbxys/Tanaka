from configparser import ConfigParser
import json
import os
from pathlib import Path

from bs4 import BeautifulSoup
from jikanpy import Jikan
from jikanpy.exceptions import APIException
from requests_ratelimiter import Duration, RequestRate, Limiter, LimiterSession

import utils

def run(base_path:Path):
    if not isinstance(base_path, Path):
        base_path = Path(base_path).resolve()
    base_path.mkdir(exist_ok=True, parents=True)

    base_url = "https://myanimelist.net/anime.php?letter={}&show={}"
    search_list = ".ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    # set rate limit for jikanpy
    mal_rate = RequestRate(1, Duration.SECOND * 4)
    limiter = Limiter(mal_rate)
    
    session = LimiterSession(limiter=limiter)
    jikan = Jikan(selected_base="https://api.jikan.moe/v4", session=session)
    
    for letter in search_list:
        search_results = 0

        while True:

            results_url = base_url.format(letter, search_results)

            # skip bad pages
            if not utils.validate_url(results_url): break

            req = session.get(results_url)    # the results page
            soup = BeautifulSoup(req.content, "html.parser")

            # Looping through each anime in the page
            for elem in soup.select("a[id^='sinfo']"):
                title = elem.select_one("strong").text
                MAL_id = utils.get_id(elem["href"])    # extract MAL id from url

                # Skip old entries
                if (base_path / f"{MAL_id}.json").exists(): continue

                try:
                    # Get information from MAL and parse it
                    MAL_metadata = jikan.anime(MAL_id)
                    MAL_metadata = utils.filter_metadata(MAL_metadata)
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
        
            # Look for the next 50 results
            search_results += 50


if __name__ == '__main__':
    config = ConfigParser()
    if not os.path.exists("config.ini"):
        config.read("example.config.ini")
    else:        
        config.read("config.ini")
    
    path = config["DB"]["Path"]
    
    run(path)