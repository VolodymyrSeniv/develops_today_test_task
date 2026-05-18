from unittest.mock import AsyncMock

import pytest

from app.application.ports.artwork_service import ArtworkData
from app.application.ports.place_repository import AbstractPlaceRepository
from app.application.ports.project_repository import AbstractProjectRepository


@pytest.fixture
def project_repo() -> AsyncMock:
    mock = AsyncMock(spec=AbstractProjectRepository)
    return mock


@pytest.fixture
def place_repo() -> AsyncMock:
    mock = AsyncMock(spec=AbstractPlaceRepository)
    return mock


@pytest.fixture
def artwork_service() -> AsyncMock:
    from app.application.ports.artwork_service import AbstractArtworkService

    mock = AsyncMock(spec=AbstractArtworkService)
    return mock


def make_artwork(id: int = 1001, title: str = "Nighthawks") -> ArtworkData:
    return ArtworkData(id=id, title=title, artist_display="Edward Hopper", image_url=None)
