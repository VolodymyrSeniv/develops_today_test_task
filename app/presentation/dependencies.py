import secrets
from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.places.add_place import AddPlaceUseCase
from app.application.use_cases.places.get_place import GetPlaceUseCase
from app.application.use_cases.places.list_places import ListPlacesUseCase
from app.application.use_cases.places.update_place import UpdatePlaceUseCase
from app.application.use_cases.projects.create_project import CreateProjectUseCase
from app.application.use_cases.projects.delete_project import DeleteProjectUseCase
from app.application.use_cases.projects.get_project import GetProjectUseCase
from app.application.use_cases.projects.list_projects import ListProjectsUseCase
from app.application.use_cases.projects.update_project import UpdateProjectUseCase
from app.infrastructure.config import get_settings
from app.infrastructure.database import AsyncSessionLocal
from app.infrastructure.external.artwork_api import ArtworkApiService
from app.infrastructure.persistence.place_repository import SQLAlchemyPlaceRepository
from app.infrastructure.persistence.project_repository import SQLAlchemyProjectRepository

settings = get_settings()
_security = HTTPBasic(auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


def require_auth(
    credentials: Annotated[HTTPBasicCredentials | None, Depends(_security)],
) -> str | None:
    if not settings.enable_auth:
        return None

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Basic"},
        )

    valid_username = secrets.compare_digest(credentials.username, settings.auth_username)
    valid_password = secrets.compare_digest(credentials.password, settings.auth_password)

    if not (valid_username and valid_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

    return credentials.username


def get_project_repo(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SQLAlchemyProjectRepository:
    return SQLAlchemyProjectRepository(db)


def get_place_repo(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SQLAlchemyPlaceRepository:
    return SQLAlchemyPlaceRepository(db)


def get_artwork_service() -> ArtworkApiService:
    return ArtworkApiService()


def get_create_project_use_case(
    project_repo: Annotated[SQLAlchemyProjectRepository, Depends(get_project_repo)],
    place_repo: Annotated[SQLAlchemyPlaceRepository, Depends(get_place_repo)],
    artwork_service: Annotated[ArtworkApiService, Depends(get_artwork_service)],
) -> CreateProjectUseCase:
    return CreateProjectUseCase(project_repo, place_repo, artwork_service)


def get_list_projects_use_case(
    project_repo: Annotated[SQLAlchemyProjectRepository, Depends(get_project_repo)],
) -> ListProjectsUseCase:
    return ListProjectsUseCase(project_repo)


def get_get_project_use_case(
    project_repo: Annotated[SQLAlchemyProjectRepository, Depends(get_project_repo)],
) -> GetProjectUseCase:
    return GetProjectUseCase(project_repo)


def get_update_project_use_case(
    project_repo: Annotated[SQLAlchemyProjectRepository, Depends(get_project_repo)],
) -> UpdateProjectUseCase:
    return UpdateProjectUseCase(project_repo)


def get_delete_project_use_case(
    project_repo: Annotated[SQLAlchemyProjectRepository, Depends(get_project_repo)],
) -> DeleteProjectUseCase:
    return DeleteProjectUseCase(project_repo)


def get_add_place_use_case(
    project_repo: Annotated[SQLAlchemyProjectRepository, Depends(get_project_repo)],
    place_repo: Annotated[SQLAlchemyPlaceRepository, Depends(get_place_repo)],
    artwork_service: Annotated[ArtworkApiService, Depends(get_artwork_service)],
) -> AddPlaceUseCase:
    return AddPlaceUseCase(project_repo, place_repo, artwork_service)


def get_list_places_use_case(
    project_repo: Annotated[SQLAlchemyProjectRepository, Depends(get_project_repo)],
    place_repo: Annotated[SQLAlchemyPlaceRepository, Depends(get_place_repo)],
) -> ListPlacesUseCase:
    return ListPlacesUseCase(project_repo, place_repo)


def get_get_place_use_case(
    project_repo: Annotated[SQLAlchemyProjectRepository, Depends(get_project_repo)],
    place_repo: Annotated[SQLAlchemyPlaceRepository, Depends(get_place_repo)],
) -> GetPlaceUseCase:
    return GetPlaceUseCase(project_repo, place_repo)


def get_update_place_use_case(
    project_repo: Annotated[SQLAlchemyProjectRepository, Depends(get_project_repo)],
    place_repo: Annotated[SQLAlchemyPlaceRepository, Depends(get_place_repo)],
) -> UpdatePlaceUseCase:
    return UpdatePlaceUseCase(project_repo, place_repo)
