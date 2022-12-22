from argparse import ArgumentParser
import json
import os
from pathlib import Path

from requests_ratelimiter import Duration, RequestRate, Limiter, LimiterSession

from utils.logging import get_logger

LOGGER = get_logger(__name__, write_to_file=True)

DEFAULT_PAGE_LIMIT = 5  # max number of pages to search
VERSION = 4

def main(a:ArgumentParser):
    args = a.parse_args()

    dest = Path(args.destination)

    scrap_media(
        base_path=dest, page_limit=args.page_limit,
        media_type=args.media_type, 
        all_=args.all
    )

def get_mal_session() -> LimiterSession:
    mal_rate = RequestRate(1, Duration.SECOND * 4)
    limiter = Limiter(mal_rate)
    session = LimiterSession(limiter=limiter)
    return session

def scrap_media(
        base_path:Path,
        page_limit:int=DEFAULT_PAGE_LIMIT,
        media_type:str="anime",
        sort_by:str="mal_id", reverse:bool=True,
        all_:bool=False):
    
    # Some maybe too lazy to manually create the directory.
    # There is advanced file path verification, so a misspell
    # can cause files to be saved in the wrong directory.
    if not isinstance(base_path, Path):
        base_path = base_path.resolve()
    base_path.mkdir(exist_ok=True, parents=True)

    jikan_endpoint = "https://api.jikan.moe/v{version}/{media_type}".format(
        version = VERSION,
        media_type = media_type
    )
    jikan_params = {
        "page": 1,
        "order_by": sort_by,
        "sort": "desc" if reverse else "asc"
    }

    # Create session compliant with Jikan API
    session = get_mal_session()

    # If not looking at all pages, set a limit for how many
    # pages to look at.
    while all_ or (jikan_params["page"] <= page_limit):
        req = session.get(jikan_endpoint, params=jikan_params)
        resp = req.json()

        current_page = resp["pagination"]["current_page"]
        has_next_page = resp["pagination"]["has_next_page"]

        for MAL_metadata in resp["data"]:
            MAL_id = MAL_metadata["mal_id"]
            title = MAL_metadata["title"]

            dest_path = base_path / f"{MAL_id}.json"

            # Skip old entries only if looking at new entries
            if all_ != True and dest_path.exists():
                # LOGGER.debug(f'Skipped {MAL_id:<6} | <{title}>...')
                continue
            
            try:
                # Write the metadata to a json file, using the MAL id as the
                # filename.
                with (base_path / f"{MAL_id}.json").open("w+", encoding="utf-8") as outfile:
                    outfile.write(json.dumps(MAL_metadata, indent=4, ensure_ascii=False))

                if all_ and dest_path.exists():
                    # Updating existing media entry
                    LOGGER.info(f'Updated {MAL_id:<6} | <{title}>...')
                else:
                    # Adding new media entry
                    LOGGER.info(f'Scrapped {MAL_id:<6} | <{title}>...')
            except KeyboardInterrupt:
                # Manual terminal of program
                LOGGER.error("Program interrupted by keyboard shorcut.")
                raise
            except Exception:
                # Ensure incomplete files are deleted.
                LOGGER.error("Dumping interrupted. Deleting file.")
                if (base_path / f"{MAL_id}.json").exists():
                    os.remove((base_path / f"{MAL_id}.json"))
                raise

        if has_next_page:
            jikan_params["page"] = current_page + 1
        else:
            break


if __name__ == '__main__':
    parser = ArgumentParser()

    parser.add_argument(
        "media_type", choices=["anime", "manga"],
        help="what type of media"
    )
    parser.add_argument(
        "-d", "--destination", type=str, required=True,
        help="where to save files"
    )
    parser.add_argument(
        "-p", "--page_limit", type=int, default=DEFAULT_PAGE_LIMIT,
        required=False, help="number of pages to look at"
    )
    parser.add_argument(
        "-a", "--all", action="store_true",
        help="look for all or only new"
    )

    main(parser)