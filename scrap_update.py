import json
import os
from pathlib import Path

from bs4 import BeautifulSoup
import requests

from MyAnimeListPy import MyAnimeList
import MyAnimeListPy.utils
import anilist_query as al_query
from MyAnimeListPy.utils.download import download


def run():
    base_path = Path("./db/mal_files v1/")
    base_path.mkdir(exist_ok=True, parents=True)

    base_url = "https://myanimelist.net/anime.php?o=9&c%5B0%5D=a&c%5B1%5D=d&cv=2&w=1&show={}"

    mal_client = MyAnimeList(None)
    
    # for letter in search_list:
    search_results = 0
    results_url = base_url

    while True:

        results_url = results_url.format(search_results)

        # skip bad pages
        if not mal_client.validate_url(results_url): return

        req = download(results_url, mal_client.session, mal_client.rate_limit)    # the results page
        soup = BeautifulSoup(req.content, "html.parser")

        # Looping through each anime in the page
        for elem in soup.select("a[id^='sinfo']"):
            print("------------------------")
            title = elem.select_one("strong").text
            MAL_id = MyAnimeListPy.utils.get_id(elem["href"])    # extract MAL id from url

            # Skip old entries
            if (base_path / f"{MAL_id}.json").exists():
                print(f"Scrapped all new entries.\nQuitting program...")
                return

            # Get information from MAL and parse it
            print(f'Scrapping from MAL "{MAL_id}" | <{title}>...')
            MAL_metadata = mal_client.get_anime(MAL_id).gather_data()

            # Use MAL id to query AniList.co.
            print(f'Querying Anilist.co for <{title}>...')
            AL_metadata = al_query.query_idMal(MAL_id)

            # Combine MAL and AniList metadata (create function to do so).
            all_metadata = MyAnimeListPy.utils.combine_sources(MAL_metadata, AL_metadata)

            try:
                # Write the metadata to a json file, using the MAL id as the
                # filename.
                print(f"Dumping <{title}>...")
                with (base_path / f"{MAL_id}.json").open("w+", encoding="utf-8") as outfile:
                    outfile.write(json.dumps(all_metadata, indent=4, ensure_ascii=False))
            except Exception as e:
                # Ensure incomplete files are deleted.
                print("Dumping interrupted. Deleting file.")
                if (base_path / f"{MAL_id}.json").exists():
                    os.remove((base_path / f"{MAL_id}.json"))
                raise e
    
        # Look for the next 50 results
        search_results += 50


if __name__ == '__main__':
    run()