from math import ceil
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.project_repository import AbstractProjectRepository, CreateProjectData
from app.domain.entities.place import Place
from app.domain.entities.project import Project
from app.infrastructure.persistence.models import PlaceModel, ProjectModel


class SQLAlchemyProjectRepository(AbstractProjectRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _place_to_domain(m: PlaceModel) -> Place:
        return Place(
            id=m.id,
            project_id=m.project_id,
            external_id=m.external_id,
            title=m.title,
            artist_display=m.artist_display,
            image_url=m.image_url,
            notes=m.notes,
            is_visited=m.is_visited,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )

    @staticmethod
    def _to_domain(m: ProjectModel) -> Project:
        return Project(
            id=m.id,
            name=m.name,
            description=m.description,
            start_date=m.start_date,
            is_completed=m.is_completed,
            created_at=m.created_at,
            updated_at=m.updated_at,
            places=[SQLAlchemyProjectRepository._place_to_domain(p) for p in m.places],
        )

    async def get_by_id(self, project_id: int) -> Project | None:
        result = await self._session.execute(
            select(ProjectModel).where(ProjectModel.id == project_id)
        )
        model = result.scalars().first()
        return self._to_domain(model) if model else None

    async def list(
        self,
        page: int,
        page_size: int,
        is_completed: bool | None,
    ) -> tuple[list[Project], int, int]:
        query = select(ProjectModel)
        count_query = select(func.count(ProjectModel.id))

        if is_completed is not None:
            query = query.where(ProjectModel.is_completed == is_completed)
            count_query = count_query.where(ProjectModel.is_completed == is_completed)

        total: int = (await self._session.execute(count_query)).scalar_one()
        total_pages = ceil(total / page_size) if total > 0 else 0

        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size).order_by(ProjectModel.created_at.desc())
        result = await self._session.execute(query)

        return [self._to_domain(m) for m in result.scalars().all()], total, total_pages

    async def create(self, data: CreateProjectData) -> Project:
        model = ProjectModel(
            name=data.name,
            description=data.description,
            start_date=data.start_date,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def update(self, project_id: int, delta: dict[str, Any]) -> Project:
        result = await self._session.execute(
            select(ProjectModel).where(ProjectModel.id == project_id)
        )
        model = result.scalars().one()
        for key, value in delta.items():
            setattr(model, key, value)
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def delete(self, project_id: int) -> None:
        result = await self._session.execute(
            select(ProjectModel).where(ProjectModel.id == project_id)
        )
        model = result.scalars().one()
        await self._session.delete(model)
        await self._session.commit()
