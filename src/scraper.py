import logging
import random
import re
import time
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from models import Biography, Leader

log = logging.getLogger(__name__)


class WikiScraper:
    def __init__(
        self,
        user_agent: str,
        min_scrape_delay: int,
        max_scrape_delay: int,
    ) -> None:
        self._session = requests.Session()
        self._headers = {"User-Agent": user_agent}
        self._min_scrape_delay = min_scrape_delay
        self._max_scrape_delay = max_scrape_delay

    @staticmethod
    def is_wiki_url(url: str) -> bool:
        """Checks if the given URL belongs to Wikipedia domain.

        Args:
            url: The URL string to check.

        Return:
            True if the URL is a Wikipedia URL, False otherwise.
        """
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower()
            return "wikipedia.org" in domain
        except Exception as e:
            log.exception("Failed to parse the given Wikipedia ulr.", e)
            return False

    def _fetch_wiki(self, url: str):
        """Fetches the content of a given URL using the internal requests session.

        Args:
            url (str): The full URL of the resource to fetch.

        Returns:
            requests.Response: The response object if the request is successful.

        Raises:
            ValueError: If the provided error is not a valid Wikipedia domain.
            requests.exceptions.RequestException: Propagated if the request
            fails due to connection issues, timeouts, or bad HTTP
            status codes (4xx or 5xx)
        """
        if not self.is_wiki_url(url):
            raise ValueError("URL must be a Wikipedia domain.")

        time.sleep(random.uniform(self._min_scrape_delay, self._max_scrape_delay))

        try:
            res = self._session.get(url, headers=self._headers)
            res.raise_for_status()
            return res
        except requests.exceptions.RequestException:
            log.error(f"Error fetching URL:{url}")
            raise

    def _find_en_interlanguage_link(self, url: str) -> str | None:
        """Navigates to the given Wikipedia URL and finds the href value
        of an <a> tag inside an <li> tag that has the classes
        'interlanguage-link' and 'interwiki-en'.

        Args:
            url: the Wikipedia URL

        Returns:
            The english wikipedia URL (string) or None if the element is not found.
        """
        parsed_url = urlparse(url)
        if "en.wikipedia.org" in parsed_url.netloc.lower():
            return url

        res = self._fetch_wiki(url)
        soup = BeautifulSoup(res.text, "html.parser")
        selector = "li.interwiki-en.interlanguage-link a"
        target_a_tag = soup.select_one(selector)
        if target_a_tag:
            return target_a_tag.get("href")
        return None

    def get_biography(self, leader: Leader) -> Biography | None:
        """Extracts the first paragraph of a Wikipedia biography.

        Args:
            leader: The leader to get the biography for.

        Returns:
            A Biography object or None if not found.
        """
        try:
            en_wiki_link = self._find_en_interlanguage_link(leader["wikipedia_url"])
            if not en_wiki_link:
                log.warning(
                    f"No english wikipedia_url for {leader['first_name']} {leader['last_name']}"
                )
                return None

            res = self._fetch_wiki(en_wiki_link)
            soup = BeautifulSoup(res.text, "html.parser")
            first_table = soup.find("table")
            if first_table:

                def is_not_empty_p(tag):
                    return tag.name == "p" and not (
                        tag.has_attr("class") and "mw-empty-elt" in tag["class"]
                    )

                target_paragraph = first_table.find_next(is_not_empty_p)
                if target_paragraph:
                    dirty_text = target_paragraph.get_text(separator="", strip=False)
                    clean_text = self._clean_text(dirty_text)
                    # log.debug(f"target_paragraph: {target_paragraph}")
                    log.debug(f"dirty_text: {dirty_text}")
                    log.debug(f"clean_text: {clean_text}")
                    return Leader(leader_id=leader["id"], content=clean_text)
        except Exception:
            log.exception(
                f"Failed to get biography for {leader['first_name']} {leader['last_name']}"
            )
        return None

    @staticmethod
    def _clean_text(text: str) -> str:
        """Removes bracketed references and pronunciations from a string."""

        def clean_parentheses_content(match):
            content = match.group(1)

            # Remove bracketed single letters/numbers like [a], [1]
            content = re.sub(r"\[[a-zA-Z0-9]]", "", content)

            pronunciation_patterns = [
                r"/[^/]+/",  # /.../
                r"([a-zA-Z]+\s+)?pronunciation:\s*\[[^\]]+\]",  # French pronunciation: [...]
                r"[a-zA-Z]+:\s*\[[^\]]+\]",  # French: [...]
                r"van BYOO-rən",  # special case for van Buren
                r"ⓘ",  # ⓘ symbol
            ]
            pronunciation_regex = "|".join(pronunciation_patterns)

            content = re.sub(pronunciation_regex, "", content)

            # Clean up extra spaces and semicolons at the beginning
            content = content.strip()
            while content.startswith(";") or content.startswith(" "):
                content = content[1:].strip()

            return f"({content})"

        # First, remove all bracketed single letters/numbers from the whole text
        text = re.sub(r"\[[a-zA-Z0-9]]", "", text)

        # Then, process the content inside parentheses
        text = re.sub(r"\((.*?)\)", clean_parentheses_content, text)

        return text
