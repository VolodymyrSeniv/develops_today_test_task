from dataclasses import dataclass
from datetime import datetime


@dataclass
class Place:
    id: int
    project_id: int
    external_id: int
    title: str
    artist_display: str | None
    image_url: str | None
    notes: str | None
    is_visited: bool
    created_at: datetime
    updated_at: datetime
