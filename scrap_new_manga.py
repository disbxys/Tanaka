from configparser import ConfigParser
import json
import os
from pathlib import Path
import sys

from requests_ratelimiter import Duration, RequestRate, Limiter, LimiterSession

DEFAULT_PAGE_LIMIT = 5  # max number of pages to search
ITEMS_PER_PAGE = 50     # number of entries per page

def run(base_path:Path, page_limit:int=DEFAULT_PAGE_LIMIT):
    if not isinstance(base_path, Path):
        base_path = Path(base_path).resolve()
    base_path.mkdir(exist_ok=True, parents=True)

    manga_endpoint = "https://api.jikan.moe/v4/manga"

    manga_params = {
        "page": 1,
        "order_by": "mal_id",
        "sort": "desc"
    }

    # Set rate limit for Jikan API
    mal_rate = RequestRate(1, Duration.SECOND * 4)
    limiter = Limiter(mal_rate)
    
    session = LimiterSession(limiter=limiter)

    # Set a limit for how many pages to look at
    while manga_params["page"] <= page_limit:
        req = session.get(manga_endpoint, params=manga_params)
        resp = req.json()

        current_page = resp["pagination"]["current_page"]
        has_next_page = resp["pagination"]["has_next_page"]

        for manga in resp["data"]:
            MAL_id = manga["mal_id"]
            title = manga["title"]

            # Skip old entries
            if (base_path / f"{MAL_id}.json").exists(): continue

            MAL_metadata = manga
            
            try:
                # Write the metadata to a json file, using the MAL id as the
                # filename.
                with (base_path / f"{MAL_id}.json").open("w+", encoding="utf-8") as outfile:
                    outfile.write(json.dumps(MAL_metadata, indent=4, ensure_ascii=False))
                print(f'Scrapped {MAL_id:<6} | <{title}>...')
            except Exception as e:
                # Ensure incomplete files are deleted.
                print("Dumping interrupted. Deleting file.")
                if (base_path / f"{MAL_id}.json").exists():
                    os.remove((base_path / f"{MAL_id}.json"))
                raise e

        if has_next_page:
            manga_params["page"] = current_page + 1
        else:
            break


if __name__ == '__main__':
    config = ConfigParser()
    if not os.path.exists("config.ini"):
        config.read("example.config.ini")
    else:        
        config.read("config.ini")
    
    path = config["DB"]["MANGA_DOWNLOAD_PATH"]

    if len(sys.argv) > 1:
        run(path, page_limit=int(sys.argv[1]))
    else:
        run(path)