from typing import Any

from loguru import logger

from app.application.ports.place_repository import AbstractPlaceRepository
from app.application.ports.project_repository import AbstractProjectRepository
from app.domain.entities.place import Place
from app.domain.exceptions import PlaceNotFound, ProjectNotFound


class UpdatePlaceUseCase:
    def __init__(
        self,
        project_repo: AbstractProjectRepository,
        place_repo: AbstractPlaceRepository,
    ) -> None:
        self._project_repo = project_repo
        self._place_repo = place_repo

    async def execute(self, project_id: int, place_id: int, delta: dict[str, Any]) -> Place:
        project = await self._project_repo.get_by_id(project_id)
        if project is None:
            raise ProjectNotFound(f"Project {project_id} not found")

        place = await self._place_repo.get_by_id(project_id, place_id)
        if place is None:
            raise PlaceNotFound(f"Place {place_id} not found in project {project_id}")

        place = await self._place_repo.update(place_id, delta)
        logger.info("Place {} in project {} updated: {}", place_id, project_id, list(delta.keys()))

        if "is_visited" in delta:
            project = await self._project_repo.get_by_id(project_id)
            if project is None:
                raise RuntimeError(f"Project {project_id} not found after place update")
            all_visited = len(project.places) > 0 and all(p.is_visited for p in project.places)
            if all_visited != project.is_completed:
                await self._project_repo.update(project_id, {"is_completed": all_visited})
                logger.info("Project {} marked as completed={}", project_id, all_visited)

        return place
