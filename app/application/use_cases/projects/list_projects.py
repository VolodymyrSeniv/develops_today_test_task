from dataclasses import dataclass

from app.application.ports.project_repository import AbstractProjectRepository
from app.application.use_cases.common import PagedResult
from app.domain.entities.project import Project


@dataclass
class ListProjectsInput:
    page: int
    page_size: int
    is_completed: bool | None


class ListProjectsUseCase:
    def __init__(self, project_repo: AbstractProjectRepository) -> None:
        self._project_repo = project_repo

    async def execute(self, input: ListProjectsInput) -> PagedResult[Project]:
        projects, total, total_pages = await self._project_repo.list(
            page=input.page,
            page_size=input.page_size,
            is_completed=input.is_completed,
        )
        return PagedResult(
            items=projects,
            total=total,
            page=input.page,
            page_size=input.page_size,
            total_pages=total_pages,
        )
