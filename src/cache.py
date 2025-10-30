import json
import os
from typing import cast

from models import Biography, Leader


class Cache:
    """A file based cache for leaders and biographies."""

    def __init__(self, cache_dir: str = ".cache") -> None:
        """Initialize the Cache.

        Args:
            cache_dir: The directory to store the cache files in.
        """
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)

    def get_leaders(self, country: str) -> list[Leader] | None:
        """Get a list of leaders from cache.

        Args:
            country: The country code.

        Returns:
            A list of leaders, or None if not in the cache.
        """
        cache_file = os.path.join(self.cache_dir, f"{country}_leaders.json")
        if os.path.exists(cache_file):
            with open(cache_file, "r") as file:
                return [cast(Leader, leader) for leader in json.load(file)]
        return None

    def set_leaders(self, country: str, leaders: list[Leader]):
        """Saves a list of leaders to the cache.

        Args:
            country: The country code.
            leaders: A list of leaders.
        """
        cache_files = os.path.join(self.cache_dir, f"{country}_leaders.json")
        with open(cache_files, "w") as file:
            json.dump([leader for leader in leaders], file)

    def set_biography(self, biography: Biography):
        """Saves a biography to the cache.

        Args:
            biography: A leader biography.
        """
        cache_file = os.path.join(self.cache_dir, f"{biography.leader_id}_bio.json")
        with open(cache_file, "w") as file:
            json.dump(biography, file)
