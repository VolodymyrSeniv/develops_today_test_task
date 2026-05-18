from typing import Any

from loguru import logger

from app.application.ports.project_repository import AbstractProjectRepository
from app.domain.entities.project import Project
from app.domain.exceptions import ProjectNotFound


class UpdateProjectUseCase:
    def __init__(self, project_repo: AbstractProjectRepository) -> None:
        self._project_repo = project_repo

    async def execute(self, project_id: int, delta: dict[str, Any]) -> Project:
        project = await self._project_repo.get_by_id(project_id)
        if project is None:
            raise ProjectNotFound(f"Project {project_id} not found")
        result = await self._project_repo.update(project_id, delta)
        logger.info("Project {} updated: {}", project_id, list(delta.keys()))
        return result
