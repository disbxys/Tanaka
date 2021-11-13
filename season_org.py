import json
import os
from pathlib import Path

db_dir = Path("./db/mal_files")

# TODO: create a txt that contains all categorized anime

def run():
    for anime in db_dir.iterdir():
        print(anime.name)
        
        # get the metadata from the file
        with anime.open(encoding="utf-8") as infile:
            metadata = json.loads(infile.read())
        print(metadata["season"])
        print("----------------------")


if __name__ == '__main__':
    run()