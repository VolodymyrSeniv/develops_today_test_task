import pytest

from app.application.use_cases.projects.get_project import GetProjectUseCase
from app.domain.exceptions import ProjectNotFound
from tests.conftest import make_project


@pytest.fixture
def use_case(project_repo):
    return GetProjectUseCase(project_repo)


async def test_get_project_success(use_case, project_repo):
    project = make_project(id=5, name="Paris Tour")
    project_repo.get_by_id.return_value = project

    result = await use_case.execute(5)

    assert result.id == 5
    assert result.name == "Paris Tour"


async def test_get_project_not_found(use_case, project_repo):
    project_repo.get_by_id.return_value = None

    with pytest.raises(ProjectNotFound):
        await use_case.execute(99)
