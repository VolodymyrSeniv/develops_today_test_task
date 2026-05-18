import pytest

from app.application.use_cases.projects.create_project import (
    CreateProjectInput,
    CreateProjectUseCase,
    PlaceInput,
)
from app.domain.exceptions import ArtworkNotFound, DuplicatePlace, PlaceLimitExceeded
from tests.conftest import make_place, make_project
from tests.unit.conftest import make_artwork


@pytest.fixture
def use_case(project_repo, place_repo, artwork_service):
    return CreateProjectUseCase(project_repo, place_repo, artwork_service)


async def test_create_project_no_places(use_case, project_repo, place_repo, artwork_service):
    project = make_project(name="Test")
    project_repo.create.return_value = project
    project_repo.get_by_id.return_value = project

    result = await use_case.execute(
        CreateProjectInput(name="Test", description=None, start_date=None)
    )

    project_repo.create.assert_called_once()
    place_repo.create.assert_not_called()
    assert result.name == "Test"


async def test_create_project_with_places(use_case, project_repo, place_repo, artwork_service):
    place = make_place(external_id=1001)
    project = make_project(places=[place])
    project_repo.create.return_value = make_project()
    project_repo.get_by_id.return_value = project
    artwork_service.get_artwork.return_value = make_artwork(id=1001)

    result = await use_case.execute(
        CreateProjectInput(
            name="Art Tour",
            description=None,
            start_date=None,
            places=[PlaceInput(external_id=1001)],
        )
    )

    artwork_service.get_artwork.assert_called_once_with(1001)
    place_repo.create.assert_called_once()
    assert len(result.places) == 1


async def test_create_project_place_limit_exceeded(use_case):
    places = [PlaceInput(external_id=i) for i in range(11)]
    with pytest.raises(PlaceLimitExceeded):
        await use_case.execute(
            CreateProjectInput(name="Too Many", description=None, start_date=None, places=places)
        )


async def test_create_project_duplicate_places(use_case):
    places = [PlaceInput(external_id=1001), PlaceInput(external_id=1001)]
    with pytest.raises(DuplicatePlace):
        await use_case.execute(
            CreateProjectInput(name="Dup", description=None, start_date=None, places=places)
        )


async def test_create_project_invalid_artwork(use_case, project_repo, artwork_service):
    artwork_service.get_artwork.return_value = None

    with pytest.raises(ArtworkNotFound):
        await use_case.execute(
            CreateProjectInput(
                name="Bad",
                description=None,
                start_date=None,
                places=[PlaceInput(external_id=9999)],
            )
        )

    project_repo.create.assert_not_called()
