from datetime import datetime

from pydantic import BaseModel, Field


class AddPlaceRequest(BaseModel):
    external_id: int = Field(..., description="Artwork ID from the Art Institute of Chicago API")


class UpdatePlaceRequest(BaseModel):
    notes: str | None = Field(default=None, description="Personal notes about this place")
    is_visited: bool | None = Field(default=None, description="Mark this place as visited")


class PlaceResponse(BaseModel):
    id: int
    project_id: int
    external_id: int
    title: str
    artist_display: str | None
    image_url: str | None
    notes: str | None
    is_visited: bool
    created_at: datetime
    updated_at: datetime


class PaginatedPlaceResponse(BaseModel):
    items: list[PlaceResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
