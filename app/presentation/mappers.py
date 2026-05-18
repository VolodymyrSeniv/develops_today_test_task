from app.domain.entities.place import Place
from app.domain.entities.project import Project
from app.presentation.api.v1.places.schemas import PlaceResponse
from app.presentation.api.v1.projects.schemas import ProjectDetailResponse, ProjectResponse


def place_to_response(place: Place) -> PlaceResponse:
    return PlaceResponse(
        id=place.id,
        project_id=place.project_id,
        external_id=place.external_id,
        title=place.title,
        artist_display=place.artist_display,
        image_url=place.image_url,
        notes=place.notes,
        is_visited=place.is_visited,
        created_at=place.created_at,
        updated_at=place.updated_at,
    )


def project_to_response(project: Project) -> ProjectResponse:
    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        start_date=project.start_date,
        is_completed=project.is_completed,
        places_count=project.places_count,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


def project_to_detail_response(project: Project) -> ProjectDetailResponse:
    return ProjectDetailResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        start_date=project.start_date,
        is_completed=project.is_completed,
        places_count=project.places_count,
        created_at=project.created_at,
        updated_at=project.updated_at,
        places=[place_to_response(p) for p in project.places],
    )
