from dataclasses import dataclass


@dataclass
class ApiConfig:
    base_url: str
    max_retry: int
    user_agent: str
    min_scrape_delay: int
    max_scrape_delay: int


@dataclass
class AppConfig:
    api: ApiConfig
    name: str
