from dataclasses import dataclass


@dataclass
class ApiConfig:
    base_url: str
    max_retry: int


@dataclass
class AppConfig:
    api: ApiConfig
    name: str
