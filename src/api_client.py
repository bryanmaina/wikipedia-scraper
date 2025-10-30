import logging
from collections.abc import Callable
from typing import cast

import requests

from models import Countries, Leader

log = logging.getLogger(__name__)


class ApiClient:
    def __init__(self, base_url: str, max_retry: int):
        """
        Initialize the ApiClient.

        Args:
            base_url: The base URL of the API
            max_retry: The number of times a call can be retried on the API
        """
        self.base_url = base_url
        self.max_retry = max_retry
        self.session = requests.session()
        self._set_cookie()

    def _set_cookie(self) -> str:
        """Sends a request to that returns a cookie that is managed
        by our  `requests.Session` instance.
        That cookie can be used with the API on all subsequent requests.
        """
        res = self.session.get(f"{self.base_url}/cookie/")
        if res.status_code == 403:
            self._set_cookie()
        res = self.session.get(f"{self.base_url}/cookie/")
        res.raise_for_status()

    def _with_retry[T](
        self,
        callable_func: Callable[[], T],
        should_retry: Callable[[T], bool],
    ) -> T:
        """Execute a callable, retrying it after renewing the cookie if a condition is met.

        Args:
            callable_func: The function (e.g., lambda) to execute, which performs the API call.
            should_retry: A function (e.g., lambda) that takes the result of callable_func
                        and returns True if a retry(and cookie renewal) is needed.

        Returns:
            The successful result of the callable_func.
        """
        for attempt in range(self.max_retry):
            result = callable_func()
            if should_retry(result):
                if attempt == self.max - 1:
                    log.info(
                        "Max retries reached. Returning the final unseccessful result."
                    )
                    return result
                log.info(
                    f"Retry condition met (Attempt {attempt + 1}). Attempting to renew cookie."
                )
                try:
                    self._set_cookie()
                except requests.HTTPError as e:
                    log.fatal(f"Failed to set a new cookie durring retry: {e}")
                    raise e
                continue
            if result.status_code >= 400:
                result.raise_for_status()
            return result

    def get_countries(self) -> Countries:
        """Gets a list of available country codes."""

        def api_call() -> requests.Response:
            return self.session.get(f"{self.base_url}/countries")

        res = self._with_retry(
            callable_func=api_call,
            should_retry=lambda response: response.status_code in [401, 403],
        )
        return cast(Countries, res.json())

    def get_leaders(self, country: str) -> list[Leader]:
        """Gets a list of leaders for a given country."""

        def api_call() -> requests.Response:
            return self.session.get(
                f"{self.base_url}/leaders",
                params={"country": country},
            )

        res = self._with_retry(
            callable_func=api_call,
            should_retry=lambda response: response.status_code in [401, 403],
        )
        leaders: list[Leader] = []
        for leader_data in res.json():
            leader_data["country"] = country
            leader = cast(Leader, leader_data)
            leaders.append(leader)
        return leaders
