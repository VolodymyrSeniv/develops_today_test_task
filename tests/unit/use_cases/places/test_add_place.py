import pytest

from app.application.use_cases.places.add_place import AddPlaceInput, AddPlaceUseCase
from app.domain.exceptions import (
    ArtworkNotFound,
    DuplicatePlace,
    PlaceLimitExceeded,
    ProjectNotFound,
)
from tests.conftest import make_place, make_project
from tests.unit.conftest import make_artwork


@pytest.fixture
def use_case(project_repo, place_repo, artwork_service):
    return AddPlaceUseCase(project_repo, place_repo, artwork_service)


async def test_add_place_success(use_case, project_repo, place_repo, artwork_service):
    project_repo.get_by_id.return_value = make_project()
    place_repo.count_for_project.return_value = 2
    place_repo.get_by_external_id.return_value = None
    artwork_service.get_artwork.return_value = make_artwork(id=1001)
    place_repo.create.return_value = make_place(external_id=1001)

    result = await use_case.execute(1, AddPlaceInput(external_id=1001))

    place_repo.create.assert_called_once()
    assert result.external_id == 1001


async def test_add_place_project_not_found(use_case, project_repo):
    project_repo.get_by_id.return_value = None

    with pytest.raises(ProjectNotFound):
        await use_case.execute(99, AddPlaceInput(external_id=1001))


async def test_add_place_limit_exceeded(use_case, project_repo, place_repo):
    project_repo.get_by_id.return_value = make_project()
    place_repo.count_for_project.return_value = 10

    with pytest.raises(PlaceLimitExceeded):
        await use_case.execute(1, AddPlaceInput(external_id=1001))


async def test_add_place_duplicate(use_case, project_repo, place_repo):
    project_repo.get_by_id.return_value = make_project()
    place_repo.count_for_project.return_value = 3
    place_repo.get_by_external_id.return_value = make_place(external_id=1001)

    with pytest.raises(DuplicatePlace):
        await use_case.execute(1, AddPlaceInput(external_id=1001))


async def test_add_place_artwork_not_found(use_case, project_repo, place_repo, artwork_service):
    project_repo.get_by_id.return_value = make_project()
    place_repo.count_for_project.return_value = 3
    place_repo.get_by_external_id.return_value = None
    artwork_service.get_artwork.return_value = None

    with pytest.raises(ArtworkNotFound):
        await use_case.execute(1, AddPlaceInput(external_id=9999))

    place_repo.create.assert_not_called()
