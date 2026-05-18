from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from typing import Any

from app.domain.entities.project import Project


@dataclass
class CreateProjectData:
    name: str
    description: str | None
    start_date: date | None


class AbstractProjectRepository(ABC):
    @abstractmethod
    async def get_by_id(self, project_id: int) -> Project | None: ...

    @abstractmethod
    async def list(
        self,
        page: int,
        page_size: int,
        is_completed: bool | None,
    ) -> tuple[list[Project], int, int]: ...

    @abstractmethod
    async def create(self, data: CreateProjectData) -> Project: ...

    @abstractmethod
    async def update(self, project_id: int, delta: dict[str, Any]) -> Project: ...

    @abstractmethod
    async def delete(self, project_id: int) -> None: ...
