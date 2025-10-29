from dataclasses import dataclass


@dataclass
class ApiConfig:
    url: str


@dataclass
class CookieConfig:
    max_age: int  # in secondes
    path: str


@dataclass
class AppConfig:
    api: ApiConfig
    cookie: CookieConfig
    name: str
