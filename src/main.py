import logging

import hydra
from hydra.core.config_store import ConfigStore

from api_client import ApiClient
from cache import Cache
from conf.config import AppConfig
from models import Leader

cs = ConfigStore.instance()
cs.store(name="base_config", node=AppConfig)

log = logging.getLogger(__name__)


@hydra.main(version_base=None, config_path="conf", config_name="config")
def main(cfg: AppConfig):
    log.info(f"Stating '{cfg.name}'!")

    api_client = ApiClient(
        base_url=cfg.api.base_url,
        max_retry=cfg.api.max_retry,
        user_agent=cfg.api.user_agent,
    )

    cache = Cache()

    countries = api_client.get_countries()
    all_leaders: list[Leader] = []
    for country in countries:
        leaders = cache.get_leaders(country)
        if not leaders:
            leaders: list[Leader] = api_client.get_leaders(country)
            cache.set_leaders(country, leaders)
        all_leaders.extend(leaders)


if __name__ == "__main__":
    main()
