import pytest

from app.application.use_cases.places.get_place import GetPlaceUseCase
from app.domain.exceptions import PlaceNotFound, ProjectNotFound
from tests.conftest import make_place, make_project


@pytest.fixture
def use_case(project_repo, place_repo):
    return GetPlaceUseCase(project_repo, place_repo)


async def test_get_place_success(use_case, project_repo, place_repo):
    project_repo.get_by_id.return_value = make_project()
    place_repo.get_by_id.return_value = make_place(id=3, title="American Gothic")

    result = await use_case.execute(1, 3)

    assert result.id == 3
    assert result.title == "American Gothic"


async def test_get_place_project_not_found(use_case, project_repo):
    project_repo.get_by_id.return_value = None

    with pytest.raises(ProjectNotFound):
        await use_case.execute(99, 1)


async def test_get_place_not_found(use_case, project_repo, place_repo):
    project_repo.get_by_id.return_value = make_project()
    place_repo.get_by_id.return_value = None

    with pytest.raises(PlaceNotFound):
        await use_case.execute(1, 99)
