import json
import os
from pathlib import Path

DEFAULT_DB_DIR = Path("./db/mal_files")
DEFAULT_SEASON_DIR = Path("./db/seasons")

# TODO: create a txt that contains all categorized anime

def sort_seasons(db_dir=DEFAULT_DB_DIR, season_dir=DEFAULT_SEASON_DIR):
    for anime in db_dir.iterdir():
        print(anime.name)
        
        # get the metadata from the file
        with anime.open(encoding="utf-8") as infile:
            metadata = json.loads(infile.read())

        # Form a filepath based on the anime season and year
        if None in metadata["season"].values():
            new_location = season_dir / 'unsorted'
        else:
            new_location = season_dir / (f'{metadata["season"]["year"]}/{metadata["season"]["season"].lower()}')
        print(new_location)

        new_location.mkdir(exist_ok=True, parents=True)

        os.rename(anime, new_location / anime.name)
        
        print("----------------------")
        return


if __name__ == '__main__':
    sort_seasons()