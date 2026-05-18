import pytest

from app.application.use_cases.places.list_places import ListPlacesInput, ListPlacesUseCase
from app.domain.exceptions import ProjectNotFound
from tests.conftest import make_place, make_project


@pytest.fixture
def use_case(project_repo, place_repo):
    return ListPlacesUseCase(project_repo, place_repo)


async def test_list_places_success(use_case, project_repo, place_repo):
    places = [make_place(id=i, external_id=1000 + i) for i in range(1, 4)]
    project_repo.get_by_id.return_value = make_project()
    place_repo.list.return_value = (places, 3, 1)

    result = await use_case.execute(1, ListPlacesInput(page=1, page_size=10, is_visited=None))

    assert result.total == 3
    assert len(result.items) == 3
    place_repo.list.assert_called_once_with(project_id=1, page=1, page_size=10, is_visited=None)


async def test_list_places_project_not_found(use_case, project_repo):
    project_repo.get_by_id.return_value = None

    with pytest.raises(ProjectNotFound):
        await use_case.execute(99, ListPlacesInput(page=1, page_size=10, is_visited=None))
