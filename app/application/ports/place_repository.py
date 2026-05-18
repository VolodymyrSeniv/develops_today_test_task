from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from app.domain.entities.place import Place


@dataclass
class CreatePlaceData:
    project_id: int
    external_id: int
    title: str
    artist_display: str | None
    image_url: str | None


class AbstractPlaceRepository(ABC):
    @abstractmethod
    async def get_by_id(self, project_id: int, place_id: int) -> Place | None: ...

    @abstractmethod
    async def get_by_external_id(self, project_id: int, external_id: int) -> Place | None: ...

    @abstractmethod
    async def list(
        self,
        project_id: int,
        page: int,
        page_size: int,
        is_visited: bool | None,
    ) -> tuple[list[Place], int, int]: ...

    @abstractmethod
    async def count_for_project(self, project_id: int) -> int: ...

    @abstractmethod
    async def create(self, data: CreatePlaceData) -> Place: ...

    @abstractmethod
    async def update(self, place_id: int, delta: dict[str, Any]) -> Place: ...
