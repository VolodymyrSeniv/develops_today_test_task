from dataclasses import dataclass

from loguru import logger

from app.application.ports.artwork_service import AbstractArtworkService
from app.application.ports.place_repository import AbstractPlaceRepository, CreatePlaceData
from app.application.ports.project_repository import AbstractProjectRepository
from app.domain.constants import MAX_PLACES_PER_PROJECT
from app.domain.entities.place import Place
from app.domain.exceptions import (
    ArtworkNotFound,
    DuplicatePlace,
    PlaceLimitExceeded,
    ProjectNotFound,
)


@dataclass
class AddPlaceInput:
    external_id: int


class AddPlaceUseCase:
    def __init__(
        self,
        project_repo: AbstractProjectRepository,
        place_repo: AbstractPlaceRepository,
        artwork_service: AbstractArtworkService,
    ) -> None:
        self._project_repo = project_repo
        self._place_repo = place_repo
        self._artwork_service = artwork_service

    async def execute(self, project_id: int, cmd: AddPlaceInput) -> Place:
        project = await self._project_repo.get_by_id(project_id)
        if project is None:
            raise ProjectNotFound(f"Project {project_id} not found")

        current_count = await self._place_repo.count_for_project(project_id)
        if current_count >= MAX_PLACES_PER_PROJECT:
            raise PlaceLimitExceeded(
                f"Project already has the maximum of {MAX_PLACES_PER_PROJECT} places"
            )

        existing = await self._place_repo.get_by_external_id(project_id, cmd.external_id)
        if existing is not None:
            raise DuplicatePlace("This artwork is already added to the project")

        artwork = await self._artwork_service.get_artwork(cmd.external_id)
        if artwork is None:
            raise ArtworkNotFound(
                f"Artwork with ID {cmd.external_id} not found in Art Institute of Chicago API"
            )

        place = await self._place_repo.create(
            CreatePlaceData(
                project_id=project_id,
                external_id=artwork.id,
                title=artwork.title,
                artist_display=artwork.artist_display,
                image_url=artwork.image_url,
            )
        )
        logger.info("Place {} ('{}') added to project {}", place.id, place.title, project_id)
        return place
