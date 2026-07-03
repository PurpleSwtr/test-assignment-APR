from dataclasses import dataclass
from datetime import datetime


@dataclass
class PostData:
    id: int
    text: str
    rubrics: list[str]
    created_date: datetime
