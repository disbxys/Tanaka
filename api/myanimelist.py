from typing import Union, Dict
from urllib.parse import urljoin

import requests
from requests_ratelimiter import Duration, RequestRate, Limiter, LimiterSession

from utils.logging import get_logger

VERSION = 4

DEFAULT_REQUEST_PARAMS = {
    "page": 1,
    "order_by": "mal_id",
    "sort": "desc"
}

class JikanController:
    logger = get_logger(__name__, write_to_file=True)
    BASE_ENDPOINT = "https://api.jikan.moe"

    def __init__(
            self,
            base_endpoint:str=BASE_ENDPOINT,
            version:Union[int, str]=VERSION,
            request_params:Dict[str, Union[str, int]]=None,
            session:requests.Session=None) -> None:
        self.logger.debug("Initializing Jikan Controller.")

        self.base_endpoint = base_endpoint
        self.version = version

        if request_params == None:
            self.logger.debug("Using default request parameters.")
            self.request_params = DEFAULT_REQUEST_PARAMS
        else:
            self.logger.debug("Using passed in request parameters.")
            self.request_params = request_params

        self.session = session if session != None else self._create_session()

    def request(self, media_type:str="anime") -> requests.Response:
        """
        Given a media type (i.e. anime, manga, etc.), make a request to
        the Jikan API search endpoint to get a list of entries.
        """
        jikan_endpoint = urljoin(
            self.base_endpoint,
            "v{version}/{media_type}".format(
                version=self.version,
                media_type=media_type
            )
        )

        try:
            req = self.session.get(jikan_endpoint, params=self.request_params)
        except:
            self.logger.warning("Unexpected error encountered!")
            raise
        
        return req

    def update_request_params(self, params:Dict[str, Union[str, int]]) -> None:
        """
        Updates requests params with the passed in params
        """
        self.request_params.update(params)
        self.logger.debug("Request parameters have been updated.")
        return

    def replace_request_params(self, params:Dict[str, Union[str, int]]) -> None:
        """
        Replaces requests params with the passed in params
        """
        self.request_params = params
        self.logger.debug("Request parameters have been replaced.")
        return

    def _create_session(self) -> LimiterSession:
        mal_rate = RequestRate(1, Duration.SECOND * 4)
        limiter = Limiter(mal_rate)
        return LimiterSession(limiter=limiter)