import logging

import hydra
from hydra.core.config_store import ConfigStore

from conf.config import AppConfig

cs = ConfigStore.instance()
cs.store(name="base_config", node=AppConfig)

log = logging.getLogger(__name__)


@hydra.main(version_base=None, config_path="conf", config_name="config")
def main(cfg: AppConfig):
    log.info(f"Stating '{cfg.name}'!")


if __name__ == "__main__":
    main()
