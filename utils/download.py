import time

import requests


def download(url, driver=requests.session(), wait_time=2):
    req = driver.get(url)
    time.sleep(wait_time)

    return req