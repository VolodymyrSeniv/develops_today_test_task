from app.application.ports.project_repository import AbstractProjectRepository
from app.domain.entities.project import Project
from app.domain.exceptions import ProjectNotFound


class GetProjectUseCase:
    def __init__(self, project_repo: AbstractProjectRepository) -> None:
        self._project_repo = project_repo

    async def execute(self, project_id: int) -> Project:
        project = await self._project_repo.get_by_id(project_id)
        if project is None:
            raise ProjectNotFound(f"Project {project_id} not found")
        return project
