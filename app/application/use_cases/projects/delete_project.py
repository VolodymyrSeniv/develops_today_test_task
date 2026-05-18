from loguru import logger

from app.application.ports.project_repository import AbstractProjectRepository
from app.domain.exceptions import ProjectHasVisitedPlaces, ProjectNotFound


class DeleteProjectUseCase:
    def __init__(self, project_repo: AbstractProjectRepository) -> None:
        self._project_repo = project_repo

    async def execute(self, project_id: int) -> None:
        project = await self._project_repo.get_by_id(project_id)
        if project is None:
            raise ProjectNotFound(f"Project {project_id} not found")

        if any(place.is_visited for place in project.places):
            raise ProjectHasVisitedPlaces("Cannot delete a project that has visited places")

        await self._project_repo.delete(project_id)
        logger.info("Project {} deleted", project_id)
