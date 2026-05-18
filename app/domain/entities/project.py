from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime

from app.domain.entities.place import Place


@dataclass
class Project:
    id: int
    name: str
    description: str | None
    start_date: date | None
    is_completed: bool
    created_at: datetime
    updated_at: datetime
    places: list[Place] = field(default_factory=list)

    @property
    def places_count(self) -> int:
        return len(self.places)
