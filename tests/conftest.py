from datetime import UTC, datetime

from app.domain.entities.place import Place
from app.domain.entities.project import Project


def make_project(
    id: int = 1,
    name: str = "Test Project",
    description: str | None = None,
    is_completed: bool = False,
    places: list[Place] | None = None,
) -> Project:
    now = datetime.now(UTC)
    return Project(
        id=id,
        name=name,
        description=description,
        start_date=None,
        is_completed=is_completed,
        created_at=now,
        updated_at=now,
        places=places or [],
    )


def make_place(
    id: int = 1,
    project_id: int = 1,
    external_id: int = 1001,
    title: str = "Nighthawks",
    is_visited: bool = False,
    notes: str | None = None,
) -> Place:
    now = datetime.now(UTC)
    return Place(
        id=id,
        project_id=project_id,
        external_id=external_id,
        title=title,
        artist_display="Edward Hopper",
        image_url=None,
        notes=notes,
        is_visited=is_visited,
        created_at=now,
        updated_at=now,
    )
