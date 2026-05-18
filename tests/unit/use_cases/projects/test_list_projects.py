from app.application.use_cases.projects.list_projects import ListProjectsInput, ListProjectsUseCase
from tests.conftest import make_project


async def test_list_projects_returns_paged_result(project_repo):
    projects = [make_project(id=i, name=f"Project {i}") for i in range(1, 4)]
    project_repo.list.return_value = (projects, 3, 1)

    use_case = ListProjectsUseCase(project_repo)
    result = await use_case.execute(ListProjectsInput(page=1, page_size=10, is_completed=None))

    assert result.total == 3
    assert result.total_pages == 1
    assert len(result.items) == 3
    project_repo.list.assert_called_once_with(page=1, page_size=10, is_completed=None)


async def test_list_projects_filters_completed(project_repo):
    project_repo.list.return_value = ([], 0, 0)

    use_case = ListProjectsUseCase(project_repo)
    await use_case.execute(ListProjectsInput(page=1, page_size=10, is_completed=True))

    project_repo.list.assert_called_once_with(page=1, page_size=10, is_completed=True)
