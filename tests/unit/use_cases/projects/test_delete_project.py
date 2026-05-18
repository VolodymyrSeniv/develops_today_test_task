import pytest

from app.application.use_cases.projects.delete_project import DeleteProjectUseCase
from app.domain.exceptions import ProjectHasVisitedPlaces, ProjectNotFound
from tests.conftest import make_place, make_project


@pytest.fixture
def use_case(project_repo):
    return DeleteProjectUseCase(project_repo)


async def test_delete_project_success(use_case, project_repo):
    project_repo.get_by_id.return_value = make_project()

    await use_case.execute(1)

    project_repo.delete.assert_called_once_with(1)


async def test_delete_project_not_found(use_case, project_repo):
    project_repo.get_by_id.return_value = None

    with pytest.raises(ProjectNotFound):
        await use_case.execute(99)

    project_repo.delete.assert_not_called()


async def test_delete_project_with_visited_place_raises(use_case, project_repo):
    visited_place = make_place(is_visited=True)
    project_repo.get_by_id.return_value = make_project(places=[visited_place])

    with pytest.raises(ProjectHasVisitedPlaces):
        await use_case.execute(1)

    project_repo.delete.assert_not_called()
