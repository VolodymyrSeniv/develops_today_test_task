from datetime import date, datetime

from pydantic import BaseModel, Field, field_validator

from app.presentation.api.v1.places.schemas import PlaceResponse

MAX_PLACES_PER_PROJECT = 10


class PlaceRefRequest(BaseModel):
    external_id: int = Field(..., description="Artwork ID from the Art Institute of Chicago API")


class CreateProjectRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    start_date: date | None = None
    places: list[PlaceRefRequest] | None = Field(
        default=None,
        description="Optional artwork places to include on creation (max 10)",
    )

    @field_validator("places")
    @classmethod
    def validate_places_count(cls, v: list[PlaceRefRequest] | None) -> list[PlaceRefRequest] | None:
        if v is not None and len(v) > MAX_PLACES_PER_PROJECT:
            raise ValueError(f"A project can have at most {MAX_PLACES_PER_PROJECT} places")
        return v


class UpdateProjectRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    start_date: date | None = None


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: str | None
    start_date: date | None
    is_completed: bool
    places_count: int
    created_at: datetime
    updated_at: datetime


class ProjectDetailResponse(ProjectResponse):
    places: list[PlaceResponse]


class PaginatedProjectResponse(BaseModel):
    items: list[ProjectResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
