from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.application.use_cases.projects.create_project import (
    CreateProjectInput,
    CreateProjectUseCase,
    PlaceInput,
)
from app.application.use_cases.projects.delete_project import DeleteProjectUseCase
from app.application.use_cases.projects.get_project import GetProjectUseCase
from app.application.use_cases.projects.list_projects import ListProjectsInput, ListProjectsUseCase
from app.application.use_cases.projects.update_project import UpdateProjectUseCase
from app.domain.exceptions import (
    ArtworkNotFound,
    DuplicatePlace,
    PlaceLimitExceeded,
    ProjectHasVisitedPlaces,
    ProjectNotFound,
)
from app.presentation.api.v1.projects.schemas import (
    CreateProjectRequest,
    PaginatedProjectResponse,
    ProjectDetailResponse,
    UpdateProjectRequest,
)
from app.presentation.dependencies import (
    get_create_project_use_case,
    get_delete_project_use_case,
    get_get_project_use_case,
    get_list_projects_use_case,
    get_update_project_use_case,
    require_auth,
)
from app.presentation.mappers import project_to_detail_response, project_to_response

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("", summary="List travel projects")
async def list_projects(
    use_case: Annotated[ListProjectsUseCase, Depends(get_list_projects_use_case)],
    _: Annotated[str | None, Depends(require_auth)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 10,
    is_completed: Annotated[bool | None, Query(description="Filter by completion status")] = None,
) -> PaginatedProjectResponse:
    result = await use_case.execute(
        ListProjectsInput(page=page, page_size=page_size, is_completed=is_completed)
    )
    return PaginatedProjectResponse(
        items=[project_to_response(p) for p in result.items],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        total_pages=result.total_pages,
    )


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Create a travel project",
)
async def create_project(
    body: CreateProjectRequest,
    use_case: Annotated[CreateProjectUseCase, Depends(get_create_project_use_case)],
    _: Annotated[str | None, Depends(require_auth)],
) -> ProjectDetailResponse:
    try:
        project = await use_case.execute(
            CreateProjectInput(
                name=body.name,
                description=body.description,
                start_date=body.start_date,
                places=[PlaceInput(external_id=p.external_id) for p in (body.places or [])],
            )
        )
    except PlaceLimitExceeded as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    except DuplicatePlace as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    except ArtworkNotFound as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    return project_to_detail_response(project)


@router.get("/{project_id}", summary="Get a travel project")
async def get_project(
    project_id: int,
    use_case: Annotated[GetProjectUseCase, Depends(get_get_project_use_case)],
    _: Annotated[str | None, Depends(require_auth)],
) -> ProjectDetailResponse:
    try:
        project = await use_case.execute(project_id)
    except ProjectNotFound as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return project_to_detail_response(project)


@router.put("/{project_id}", summary="Update a travel project")
async def update_project(
    project_id: int,
    body: UpdateProjectRequest,
    use_case: Annotated[UpdateProjectUseCase, Depends(get_update_project_use_case)],
    _: Annotated[str | None, Depends(require_auth)],
) -> ProjectDetailResponse:
    delta = body.model_dump(exclude_unset=True)
    if not delta:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No fields provided for update",
        )
    try:
        project = await use_case.execute(project_id, delta)
    except ProjectNotFound as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return project_to_detail_response(project)


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a travel project",
)
async def delete_project(
    project_id: int,
    use_case: Annotated[DeleteProjectUseCase, Depends(get_delete_project_use_case)],
    _: Annotated[str | None, Depends(require_auth)],
) -> None:
    try:
        await use_case.execute(project_id)
    except ProjectNotFound as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ProjectHasVisitedPlaces as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
