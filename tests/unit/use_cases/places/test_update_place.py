import pytest

from app.application.use_cases.places.update_place import UpdatePlaceUseCase
from app.domain.exceptions import PlaceNotFound, ProjectNotFound
from tests.conftest import make_place, make_project


@pytest.fixture
def use_case(project_repo, place_repo):
    return UpdatePlaceUseCase(project_repo, place_repo)


async def test_update_place_notes(use_case, project_repo, place_repo):
    project_repo.get_by_id.return_value = make_project()
    place_repo.get_by_id.return_value = make_place()
    updated = make_place(notes="Amazing!")
    place_repo.update.return_value = updated

    result = await use_case.execute(1, 1, {"notes": "Amazing!"})

    place_repo.update.assert_called_once_with(1, {"notes": "Amazing!"})
    assert result.notes == "Amazing!"


async def test_update_place_mark_visited_completes_project(use_case, project_repo, place_repo):
    place = make_place(is_visited=False)
    project = make_project(places=[place])
    project_repo.get_by_id.return_value = project
    place_repo.get_by_id.return_value = place
    place_repo.update.return_value = make_place(is_visited=True)

    visited_project = make_project(places=[make_place(is_visited=True)], is_completed=False)
    project_repo.get_by_id.side_effect = [project, visited_project]

    await use_case.execute(1, 1, {"is_visited": True})

    project_repo.update.assert_called_once_with(1, {"is_completed": True})


async def test_update_place_project_not_found(use_case, project_repo):
    project_repo.get_by_id.return_value = None

    with pytest.raises(ProjectNotFound):
        await use_case.execute(99, 1, {"notes": "x"})


async def test_update_place_not_found(use_case, project_repo, place_repo):
    project_repo.get_by_id.return_value = make_project()
    place_repo.get_by_id.return_value = None

    with pytest.raises(PlaceNotFound):
        await use_case.execute(1, 99, {"notes": "x"})
