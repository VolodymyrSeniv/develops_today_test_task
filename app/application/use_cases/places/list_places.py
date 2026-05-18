from dataclasses import dataclass

from app.application.ports.place_repository import AbstractPlaceRepository
from app.application.ports.project_repository import AbstractProjectRepository
from app.application.use_cases.common import PagedResult
from app.domain.entities.place import Place
from app.domain.exceptions import ProjectNotFound


@dataclass
class ListPlacesInput:
    page: int
    page_size: int
    is_visited: bool | None


class ListPlacesUseCase:
    def __init__(
        self,
        project_repo: AbstractProjectRepository,
        place_repo: AbstractPlaceRepository,
    ) -> None:
        self._project_repo = project_repo
        self._place_repo = place_repo

    async def execute(self, project_id: int, input: ListPlacesInput) -> PagedResult[Place]:
        project = await self._project_repo.get_by_id(project_id)
        if project is None:
            raise ProjectNotFound(f"Project {project_id} not found")

        places, total, total_pages = await self._place_repo.list(
            project_id=project_id,
            page=input.page,
            page_size=input.page_size,
            is_visited=input.is_visited,
        )
        return PagedResult(
            items=places,
            total=total,
            page=input.page,
            page_size=input.page_size,
            total_pages=total_pages,
        )
