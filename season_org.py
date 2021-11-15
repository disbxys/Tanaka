import json
from pathlib import Path

DEFAULT_DB_DIR = Path("./db/mal_files")
DEFAULT_SEASON_FILE = Path("./db/season_index.json")

# TODO: create a txt that contains all categorized anime

def sort_seasons(db_dir:Path=DEFAULT_DB_DIR,
                season_file:Path=DEFAULT_SEASON_FILE,
                overwrite:bool=False):

    # Load the season index if it exists
    # else create a new one
    if season_file.exists():
        with season_file.open(encoding="utf-8") as infile:
            seasons_dict = json.loads(infile.read())
    else:
        seasons_dict = dict()

    try:
        for anime in db_dir.iterdir():            
            # get the metadata from the file
            with anime.open(encoding="utf-8") as infile:
                metadata = json.loads(infile.read())

            if metadata["idMal"] in seasons_dict.keys():
                if overwrite:
                    # Do not update if attribute is None
                    if metadata["season"]["season"] != None:
                        seasons_dict[metadata["idMal"]]["season"] = metadata["season"]["season"]
                    if metadata["season"]["year"] != None:
                        seasons_dict[metadata["idMal"]]["year"] = metadata["season"]["year"]
                elif None in seasons_dict[metadata["idMal"]]:
                    # Bypass overwrite if None detected in attributes
                    if seasons_dict[metadata["idMal"]]["season"] == None:
                        seasons_dict[metadata["idMal"]]["season"] = metadata["season"]["season"]
                    if seasons_dict[metadata["idMal"]]["year"] == None:
                        seasons_dict[metadata["idMal"]]["year"] = metadata["season"]["year"]
                else:
                    print(f"Anime <{metadata['idMal']}> has not been updated")

    except MemoryError:
        # Try to dump the seasons index to a file
        # before raising
        print("Season index exceeds memory capacity. Dumping content to file")
    finally:
        with season_file.open('w+', encoding='utf-8') as outfile:
            outfile.write(json.dumps(seasons_dict, indent=4))


if __name__ == '__main__':
    sort_seasons()