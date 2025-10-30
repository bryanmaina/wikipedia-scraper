from typing import TypedDict

from typing_extensions import ReadOnly


class Biography(TypedDict):
    leader_id: str
    content: str


class Countries(TypedDict):
    __root__: list[str]


class Leader(TypedDict, total=False):
    id: ReadOnly[str]
    first_name: ReadOnly[str]
    last_name: ReadOnly[str]
    birth_date: ReadOnly[str]
    death_data: ReadOnly[str]
    place_of_birth: ReadOnly[str]
    wikipedia_url: ReadOnly[str]
    start_mandate: ReadOnly[str]
    end_mandate: ReadOnly[str]
    country: ReadOnly[str]
