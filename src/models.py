from typing import TypedDict


class Biography(TypedDict):
    leader_id: str
    content: str


class Countries(TypedDict):
    __root__: list[str]


class Leader(TypedDict):
    id: str
    first_name: str
    last_name: str
    birth_date: str
    death_data: str
    place_of_birth: str
    wikipedia_url: str
    start_mandate: str
    end_mandate: str
    country: str
