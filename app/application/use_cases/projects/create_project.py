from dataclasses import dataclass, field
from datetime import date

from loguru import logger

from app.application.ports.artwork_service import AbstractArtworkService
from app.application.ports.place_repository import AbstractPlaceRepository, CreatePlaceData
from app.application.ports.project_repository import AbstractProjectRepository, CreateProjectData
from app.domain.constants import MAX_PLACES_PER_PROJECT
from app.domain.entities.project import Project
from app.domain.exceptions import ArtworkNotFound, DuplicatePlace, PlaceLimitExceeded


@dataclass
class PlaceInput:
    external_id: int


@dataclass
class CreateProjectInput:
    name: str
    description: str | None
    start_date: date | None
    places: list[PlaceInput] = field(default_factory=list)


class CreateProjectUseCase:
    def __init__(
        self,
        project_repo: AbstractProjectRepository,
        place_repo: AbstractPlaceRepository,
        artwork_service: AbstractArtworkService,
    ) -> None:
        self._project_repo = project_repo
        self._place_repo = place_repo
        self._artwork_service = artwork_service

    async def execute(self, cmd: CreateProjectInput) -> Project:
        if len(cmd.places) > MAX_PLACES_PER_PROJECT:
            raise PlaceLimitExceeded(f"A project can have at most {MAX_PLACES_PER_PROJECT} places")

        external_ids = [p.external_id for p in cmd.places]
        if len(external_ids) != len(set(external_ids)):
            raise DuplicatePlace("Duplicate place IDs in request")

        artworks = []
        for place_input in cmd.places:
            artwork = await self._artwork_service.get_artwork(place_input.external_id)
            if artwork is None:
                raise ArtworkNotFound(
                    f"Artwork {place_input.external_id} not found in Art Institute of Chicago API"
                )
            artworks.append(artwork)

        project = await self._project_repo.create(
            CreateProjectData(
                name=cmd.name,
                description=cmd.description,
                start_date=cmd.start_date,
            )
        )

        for artwork in artworks:
            await self._place_repo.create(
                CreatePlaceData(
                    project_id=project.id,
                    external_id=artwork.id,
                    title=artwork.title,
                    artist_display=artwork.artist_display,
                    image_url=artwork.image_url,
                )
            )

        result = await self._project_repo.get_by_id(project.id)
        if result is None:
            raise RuntimeError(f"Project {project.id} not found after creation")
        logger.info(
            "Project {} '{}' created with {} place(s)", result.id, result.name, len(result.places)
        )
        return result
