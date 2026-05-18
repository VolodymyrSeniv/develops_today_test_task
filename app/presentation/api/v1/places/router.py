from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.application.use_cases.places.add_place import AddPlaceInput, AddPlaceUseCase
from app.application.use_cases.places.get_place import GetPlaceUseCase
from app.application.use_cases.places.list_places import ListPlacesInput, ListPlacesUseCase
from app.application.use_cases.places.update_place import UpdatePlaceUseCase
from app.domain.exceptions import (
    ArtworkNotFound,
    DuplicatePlace,
    PlaceLimitExceeded,
    PlaceNotFound,
    ProjectNotFound,
)
from app.presentation.api.v1.places.schemas import (
    AddPlaceRequest,
    PaginatedPlaceResponse,
    PlaceResponse,
    UpdatePlaceRequest,
)
from app.presentation.dependencies import (
    get_add_place_use_case,
    get_get_place_use_case,
    get_list_places_use_case,
    get_update_place_use_case,
    require_auth,
)
from app.presentation.mappers import place_to_response

router = APIRouter(prefix="/projects/{project_id}/places", tags=["Places"])


@router.get("", summary="List places in a project")
async def list_places(
    project_id: int,
    use_case: Annotated[ListPlacesUseCase, Depends(get_list_places_use_case)],
    _: Annotated[str | None, Depends(require_auth)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 10,
    is_visited: Annotated[bool | None, Query(description="Filter by visited status")] = None,
) -> PaginatedPlaceResponse:
    try:
        result = await use_case.execute(
            project_id, ListPlacesInput(page=page, page_size=page_size, is_visited=is_visited)
        )
    except ProjectNotFound as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return PaginatedPlaceResponse(
        items=[place_to_response(p) for p in result.items],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        total_pages=result.total_pages,
    )


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Add a place to a project",
)
async def add_place(
    project_id: int,
    body: AddPlaceRequest,
    use_case: Annotated[AddPlaceUseCase, Depends(get_add_place_use_case)],
    _: Annotated[str | None, Depends(require_auth)],
) -> PlaceResponse:
    try:
        place = await use_case.execute(project_id, AddPlaceInput(external_id=body.external_id))
    except ProjectNotFound as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PlaceLimitExceeded as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    except DuplicatePlace as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except ArtworkNotFound as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    return place_to_response(place)


@router.get("/{place_id}", summary="Get a single place in a project")
async def get_place(
    project_id: int,
    place_id: int,
    use_case: Annotated[GetPlaceUseCase, Depends(get_get_place_use_case)],
    _: Annotated[str | None, Depends(require_auth)],
) -> PlaceResponse:
    try:
        place = await use_case.execute(project_id, place_id)
    except ProjectNotFound as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PlaceNotFound as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return place_to_response(place)


@router.patch(
    "/{place_id}",
    summary="Update notes or visited status for a place",
)
async def update_place(
    project_id: int,
    place_id: int,
    body: UpdatePlaceRequest,
    use_case: Annotated[UpdatePlaceUseCase, Depends(get_update_place_use_case)],
    _: Annotated[str | None, Depends(require_auth)],
) -> PlaceResponse:
    delta = body.model_dump(exclude_unset=True)
    if not delta:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No fields provided for update",
        )
    try:
        place = await use_case.execute(project_id, place_id, delta)
    except ProjectNotFound as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PlaceNotFound as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return place_to_response(place)
