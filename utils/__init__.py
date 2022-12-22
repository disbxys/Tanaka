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