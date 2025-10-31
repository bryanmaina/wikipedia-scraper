import json
import logging
import os

import hydra
from hydra.core.config_store import ConfigStore

from api_client import ApiClient
from cache import Cache
from conf.config import AppConfig
from models import Leader
from scraper import WikiScraper

cs = ConfigStore.instance()
cs.store(name="base_config", node=AppConfig)

log = logging.getLogger(__name__)


def get_all_leaders(api_client: ApiClient, cache: Cache) -> list[Leader]:
    """Get all the leaders from the cache or fetch them from the API."""
    countries = api_client.get_countries()
    all_leaders: list[Leader] = []
    for country in countries:
        leaders = cache.get_leaders(country)
        if not leaders:
            leaders: list[Leader] = api_client.get_leaders(country)
            cache.set_leaders(country, leaders)
        all_leaders.extend(leaders)
    return all_leaders


def scrape_biographies(wiki_scraper: WikiScraper, cache: Cache, leaders: list[Leader]):
    for leader in leaders:
        biography = cache.get_biography(leader["id"])
        if not biography:
            log.info(
                f"Scraping biography for {leader['first_name']} {leader['last_name']}"
            )
            biography = wiki_scraper.get_biography(leader)
            if biography:
                cache.set_biography(biography)


def consolidate_data(cache: Cache, leaders: list[Leader]):
    """Consolidates leader and biography data and saves it to a file."""
    all_biographies = cache.get_all_biographies()

    consolidated_leaders = []
    for leader in leaders:
        leader_id = leader["id"]
        if leader_id in all_biographies:
            leader["biography"] = all_biographies[leader_id]["content"]
        else:
            leader["biography"] = None
        consolidated_leaders.append(leader)

    with open(os.path.join(cache.cache_dir, "leaders.json"), "w") as f:
        json.dump(consolidated_leaders, f, indent=4)


@hydra.main(version_base=None, config_path="conf", config_name="config")
def main(cfg: AppConfig):
    log.info(f"Stating '{cfg.name}'!")

    api_client = ApiClient(
        base_url=cfg.api.base_url,
        max_retry=cfg.api.max_retry,
        user_agent=cfg.api.user_agent,
    )

    cache = Cache()

    all_leaders = get_all_leaders(api_client, cache)

    wiki_scraper = WikiScraper(
        user_agent=cfg.api.user_agent,
        min_scrape_delay=cfg.api.min_scrape_delay,
        max_scrape_delay=cfg.api.max_scrape_delay,
    )

    scrape_biographies(wiki_scraper, cache, all_leaders)

    consolidate_data(cache, all_leaders)

    log.info(f"Stopping '{cfg.name}'!")


if __name__ == "__main__":
    main()
