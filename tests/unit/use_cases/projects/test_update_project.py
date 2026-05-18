import pytest

from app.application.use_cases.projects.update_project import UpdateProjectUseCase
from app.domain.exceptions import ProjectNotFound
from tests.conftest import make_project


@pytest.fixture
def use_case(project_repo):
    return UpdateProjectUseCase(project_repo)


async def test_update_project_success(use_case, project_repo):
    original = make_project(name="Old Name")
    updated = make_project(name="New Name")
    project_repo.get_by_id.return_value = original
    project_repo.update.return_value = updated

    result = await use_case.execute(1, {"name": "New Name"})

    project_repo.update.assert_called_once_with(1, {"name": "New Name"})
    assert result.name == "New Name"


async def test_update_project_not_found(use_case, project_repo):
    project_repo.get_by_id.return_value = None

    with pytest.raises(ProjectNotFound):
        await use_case.execute(99, {"name": "Anything"})

    project_repo.update.assert_not_called()


async def test_update_project_partial_fields(use_case, project_repo):
    project = make_project(description="Old desc")
    project_repo.get_by_id.return_value = project
    project_repo.update.return_value = make_project(description="New desc")

    await use_case.execute(1, {"description": "New desc"})

    project_repo.update.assert_called_once_with(1, {"description": "New desc"})
