from datetime import datetime
from urllib.parse import urlparse

import requests
import requests.exceptions as rex


def get_id(url):
    '''
    Separates the path of the url and get the
    second part of the path (the MAL ID).
    Ex.
        https://myanimelist.net/anime/12031/Kingdom
        returns 12031
    '''
    return urlparse(url).path.split('/')[2]


def validate_url(url:str) -> bool:
    """Tests the connection to the given url"""
    try:
        requests.head(url).raise_for_status()
        return True
    except (rex.MissingSchema, rex.HTTPError):
        return False


def combine_sources(mal, al):
    '''
    Joins metadata from MyAnimeList and AniList
    and removes any redundant data. Returns a
    dict object containing the newly joined data.
    '''

    if "errors" in al.keys():
        # If no metadata from anilist
        return mal_all(mal)

    # For simplicity
    al = al["data"]["Media"]

    j_data = {
        "idMal": "", "idAL": None, "title": "",
        "english": [], "native": [],
        "type": "",
        "episodes": 0, "status": "",
        "aired": {
            "start": None,
            "end": None
        },
        "season": {
            "season": None,
            "year": None
        },
        "category": {
            "demographic": "",
            "theme": "",
            "genres": [],
            "tags": []
        },
        "source": "",
        "licensors": [], "studios": [],
        "rating": ""
    }

    j_data["idMal"] = mal["id"]
    j_data["idAL"] = str(al["id"])

    j_data["title"] = mal["title"]

    # Maintain a list with no duplicates
    j_data["english"] += mal.get("english", []) + mal.get("synonyms", [])
    if al["title"]["english"] != None: j_data["english"] += [al["title"]["english"]]
    if al["title"]["romaji"] != None: j_data["english"] += [al["title"]["romaji"]]
    j_data["english"] = list(set(j_data["english"]))

    if al["title"]["native"] != None:
        j_data["native"] += list(set(mal.get("japanese", []) + [al["title"]["native"]]))
    else:
        j_data["native"] += mal.get("japanese", [])

    j_data["type"] = mal["type"]

    try:
        j_data["episodes"] = int(mal["episodes"])
    except ValueError:
        j_data["episodes"] = 0

    j_data["status"] = mal["status"]

    airing_date = parse_airing_date(mal["aired"])
    j_data["aired"]["start"], j_data["aired"]["end"] = airing_date

    if al["season"] != None: j_data["season"]["season"] = al["season"]
    if al["seasonYear"] != None: j_data["season"]["year"] = al["seasonYear"]
    if (None in (al["season"], al["seasonYear"]))\
        and (j_data["aired"]["start"] != None):
        sseason, syear = date_to_season(j_data["aired"]["start"])
        j_data["season"]["season"] = sseason
        j_data["season"]["year"] = syear

    j_data["category"]["demographic"] = mal.get("demographic", "")
    j_data["category"]["theme"] = mal.get("theme", "")
    j_data["category"]["genres"] = list(set(mal["genres"] + al["genres"]))
    j_data["category"]["tags"] = [node["name"] for node in al["tags"]]
    
    j_data["source"] = mal["source"]

    if mal["licensors"] != "None found":
        if (type(mal["licensors"]) == str) and (mal["licensors"] != ""):
            j_data["licensors"].append(mal["licensors"])
        else:
            for licensor in mal["licensors"]:
                if licensor != "":
                    j_data["licensors"].append(licensor)

    for edge in al["studios"]["edges"]:
        j_data["studios"].append(edge["node"]["name"])

    j_data["rating"] = mal["rating"]

    return j_data


def mal_all(mal):
    '''
    Reformats the mal data into the same format as
    shown in the combine_sources function
    '''
    j_data = {
        "idMal": "", "idAL": None, "title": "",
        "english": [], "native": [],
        "type": "",
        "episodes": 0, "status": "",
        "aired": {
            "start": None,
            "end": None
        },
        "season": {
            "season": None,
            "year": None
        },
        "category": {
            "demographic": "",
            "theme": "",
            "genres": [],
            "tags": []
        },
        "source": "",
        "licensors": [], "studios": [],
        "rating": ""
    }

    j_data["idMal"] = mal["id"]

    j_data["title"] = mal["title"]

    # Maintain a list with no duplicates
    j_data["english"] += list(set(mal.get("english", []) \
                        + mal.get("synonyms", [])))

    j_data["native"] += mal.get("japanese", [])

    j_data["type"] = mal["type"]

    try:
        j_data["episodes"] = int(mal["episodes"])
    except ValueError:
        j_data["episodes"] = 0

    j_data["status"] = mal["status"]

    airing_date = parse_airing_date(mal["aired"])
    j_data["aired"]["start"], j_data["aired"]["end"] = airing_date

    if "premiered" in mal.keys():
        j_data["season"]["season"], j_data["season"]["year"] = mal["premiered"].split()
    elif j_data["aired"]["start"] != None:
        j_data["season"]["season"], j_data["season"]["year"] = date_to_season(j_data["aired"]["start"])

    j_data["category"]["demographic"] = mal.get("demographic", "")
    j_data["category"]["theme"] = mal.get("theme", "")
    j_data["category"]["genres"] = list(set(mal["genres"]))

    if mal["licensors"] != "None found":
        if (type(mal["licensors"]) == str) and (mal["licensors"] != ""):
            j_data["licensors"].append(mal["licensors"])
        else:
            for licensor in mal["licensors"]:
                if licensor != "":
                    j_data["licensors"].append(licensor)

    j_data["studios"] = mal.get("studios", [])

    j_data["rating"] = mal["rating"]

    return j_data


def filter_metadata(metadata:dict) -> dict:
    # Create a list of keywords to look for that do not contain relevant data
    # ban_list = [
    #     "request_hash", "request_cached", "request_cache_expiry",
    #     "API_DEPRECATION", "API_DEPRECATION_DATE", "API_DEPRECATION_INFO",
    #     "jikan_url", "headers"
    # ]

    sorted_data = dict()

    # Add each keyword not in the ban list
    for k, val in metadata["data"].items():
        # if k not in ban_list:
        sorted_data[k] = val

    return sorted_data


def parse_airing_date(airing_date):

    start_date = end_date = None

    if airing_date == "Not available": return (start_date, end_date)

    if " to " not in airing_date:
        try:
            start_date = end_date = dt_obj = str(datetime.strptime(airing_date, "%b %d, %Y").date())
        except: pass

        try:
            start_date = end_date = dt_obj = str(datetime.strptime(airing_date, "%b %Y").date())
        except: pass

        try:
            start_date = end_date = dt_obj = str(datetime.strptime(airing_date, "%Y").date())
        except:
            pass
    
    else:
        start_date, end_date = airing_date.split(" to ")

        if "?" in start_date:
            start_date = None
        else:
            try:
                start_date = dt_obj = str(datetime.strptime(start_date, "%b %d, %Y").date())
            except: pass

            try:
                start_date = dt_obj = str(datetime.strptime(start_date, "%b %Y").date())
            except: pass

            try:
                start_date = dt_obj = str(datetime.strptime(start_date, "%Y").date())
            except:
                pass

        if "?" in end_date:
            end_date = None
        else:
            try:
                end_date = dt_obj = str(datetime.strptime(end_date, "%b %d, %Y").date())
            except: pass

            try:
                end_date = dt_obj = str(datetime.strptime(end_date, "%b %Y").date())
            except: pass

            try:
                end_date = dt_obj = str(datetime.strptime(end_date, "%Y").date())
            except:
                pass

            end_date = max(start_date, end_date)

    return (start_date, end_date)


def date_to_season(d):
    '''
    Converts the date to the corresponding season and year.
    param d needs to be in format 'YYYY-MM-DD'
    '''
    
    d_obj = datetime.strptime(d, "%Y-%m-%d")
    d_year = d_obj.year # separate the year
    d_obj = (d_obj.month, d_obj.day)

    if d_obj < (3, 20):
        return ("WINTER", d_year)
    elif d_obj < (6, 21):
        return ("SPRING", d_year)
    elif d_obj < (9, 22):
        return ("SUMMER", d_year)
    elif d_obj < (12, 21):
        return ("FALL", d_year)
    elif d_obj >= (12, 21):
        # Round end-of-year winter to next year
        return ("WINTER", d_year+1)