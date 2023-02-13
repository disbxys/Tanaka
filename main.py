from argparse import ArgumentParser
import json
import os
from pathlib import Path

from requests_ratelimiter import Duration, RequestRate, Limiter, LimiterSession

from api.myanimelist import JikanController
from utils.logging import get_logger

logger = get_logger(__name__, write_to_file=True)

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
        page_limit: int = DEFAULT_PAGE_LIMIT,
        media_type: str = "anime",
        sort_by: str = "mal_id", reverse: bool = True,
        all_: bool = False):
    
    # Some maybe too lazy to manually create the directory.
    # There is advanced file path verification, so a misspell
    # can cause files to be saved in the wrong directory.
    if not isinstance(base_path, Path):
        base_path = Path(base_path).resolve()
    base_path.mkdir(exist_ok=True, parents=True)

    # Create client to access to Jikan API
    client = JikanController(version=VERSION)

    # If not looking at all pages, set a limit for how many
    # pages to look at.
    while all_ or (client.request_params["page"] <= page_limit):
        req = client.request(media_type=media_type)
        resp = req.json()

        current_page = resp["pagination"]["current_page"]
        has_next_page = resp["pagination"]["has_next_page"]

        for media_metadata in resp["data"]:
            MAL_id = media_metadata["mal_id"]
            title = media_metadata["title"]

            # Build the filepath using the MAL id as the filename
            dest_path = base_path / f"{MAL_id}.json"

            # Keep a flag to check if the media entry is new or not
            is_existing_entry = dest_path.exists()

            # Skip old entries only if looking at new entries
            if all_ != True and is_existing_entry:
                # LOGGER.debug(f'Skipped {MAL_id:<6} | <{title}>...')
                continue
            
            try:
                # Compare the data pulled to the existing copy
                # and skip if there is no difference
                if is_existing_entry:
                    with dest_path.open("r", encoding="utf-8") as infile:
                        local_data = json.load(infile)
                    
                    if media_metadata == local_data: continue

                # Dump metadata to a json file
                with dest_path.open("w+", encoding="utf-8") as outfile:
                    outfile.write(json.dumps(media_metadata, indent=4, ensure_ascii=False))

                if all_ and is_existing_entry:
                    # Updating existing media entry
                    logger.info(f'Updated {MAL_id:<6} | <{title}>...')
                else:
                    # Adding new media entry
                    logger.info(f'Scrapped {MAL_id:<6} | <{title}>...')
            except KeyboardInterrupt:
                # Manual terminal of program
                logger.error("Program interrupted by keyboard shorcut.")
                raise
            except Exception:
                # TODO: Log what type of error occured
                logger.error("Error encountered when creating file {}.".format(dest_path.name))
                raise

        if has_next_page:
            client.update_request_params({"page": current_page + 1})
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