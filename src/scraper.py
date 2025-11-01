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
        # Remove bracketed citations (e.g., [1], [2])
        text = re.sub(r"\[[^]]+\]", "", text)

        # Remove IPA and similar notations (e.g., /.../; )
        text = re.sub(r"/[^/]+/[^;]+;", "", text)

        # Remove the 'ⓘ' symbol and any trailing comma/space
        text = re.sub(r"\s*ⓘ,?", "", text)

        # Remove IPA patterns like /IPA/;
        text = re.sub(r"/[^/]+/;", "", text)

        # Remove any content within square brackets (e.g., [pronunciation])
        # This is a global removal, assuming square brackets are primarily for pronunciations or citations (already removed).
        text = re.sub(r"\[[^]]+\]", "", text)

        # Remove patterns like "Language: " that might be left over from pronunciation removal
        # This targets "Dutch: ", "French: ", etc., followed by optional punctuation and spaces.
        # This is applied globally, but should primarily affect areas where pronunciations were.
        text = re.sub(r"[A-Za-z]+(?: pronunciation)?:\s*[,;]?\s*", "", text)

        # General cleanup for parentheses and whitespace
        text = re.sub(r"\s+", " ", text).strip()  # Normalize whitespace
        text = re.sub(r"\(\s*\)", "", text)  # Remove empty parentheses
        text = re.sub(r"\s*([,.])", r"\1", text)  # Remove space before punctuation
        text = re.sub(r"\(\s*", "(", text)  # Remove space after opening parenthesis
        text = re.sub(r"\s*\)", ")", text)  # Remove space before closing parenthesis
        text = re.sub(
            r"\(,", "(", text
        )  # Remove leading comma after opening parenthesis
        text = re.sub(
            r",\s*\)", ")", text
        )  # Remove trailing comma before closing parenthesis
        text = re.sub(
            r";\s*\)", ")", text
        )  # Remove trailing semicolon before closing parenthesis
        return text
