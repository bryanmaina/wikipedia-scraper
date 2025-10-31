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

    def get_biography(self, leader_id: str) -> Biography | None:
        """Get a biography from cache.

        Args:
            leader_id: The ID of the leader.
        Returns:
            A biography, or None if not in the cache.
        """
        cache_file = os.path.join(self.cache_dir, f"{leader_id}_bio.json")
        if os.path.exists(cache_file):
            with open(cache_file, "r") as file:
                return cast(Biography, json.load(file))
        return None

    def set_biography(self, biography: Biography):
        """Saves a biography to the cache.

        Args:
            biography: A leader biography.
        """
        cache_file = os.path.join(self.cache_dir, f"{biography['leader_id']}_bio.json")
        with open(cache_file, "w") as file:
            json.dump(biography, file)

    def get_all_biographies(self) -> dict[str, Biography]:
        """Gets all biographies from the cache.

        Returns:
            A dictionary mapping leader_id to Biography objects.
        """
        all_biographies: dict[str, Biography] = {}
        for filename in os.listdir(self.cache_dir):
            if filename.endswith("_bio.json"):
                leader_id = filename.replace("_bio.json", "")
                cache_file = os.path.join(self.cache_dir, filename)
                with open(cache_file, "r") as file:
                    all_biographies[leader_id] = cast(Biography, json.load(file))
        return all_biographies
