from math import ceil
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.place_repository import AbstractPlaceRepository, CreatePlaceData
from app.domain.entities.place import Place
from app.infrastructure.persistence.models import PlaceModel


class SQLAlchemyPlaceRepository(AbstractPlaceRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _to_domain(m: PlaceModel) -> Place:
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

    async def get_by_id(self, project_id: int, place_id: int) -> Place | None:
        result = await self._session.execute(
            select(PlaceModel).where(PlaceModel.id == place_id, PlaceModel.project_id == project_id)
        )
        model = result.scalars().first()
        return self._to_domain(model) if model else None

    async def get_by_external_id(self, project_id: int, external_id: int) -> Place | None:
        result = await self._session.execute(
            select(PlaceModel).where(
                PlaceModel.project_id == project_id,
                PlaceModel.external_id == external_id,
            )
        )
        model = result.scalars().first()
        return self._to_domain(model) if model else None

    async def list(
        self,
        project_id: int,
        page: int,
        page_size: int,
        is_visited: bool | None,
    ) -> tuple[list[Place], int, int]:
        query = select(PlaceModel).where(PlaceModel.project_id == project_id)
        count_query = select(func.count(PlaceModel.id)).where(PlaceModel.project_id == project_id)

        if is_visited is not None:
            query = query.where(PlaceModel.is_visited == is_visited)
            count_query = count_query.where(PlaceModel.is_visited == is_visited)

        total: int = (await self._session.execute(count_query)).scalar_one()
        total_pages = ceil(total / page_size) if total > 0 else 0

        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size).order_by(PlaceModel.created_at.asc())
        result = await self._session.execute(query)

        return [self._to_domain(m) for m in result.scalars().all()], total, total_pages

    async def count_for_project(self, project_id: int) -> int:
        result = await self._session.execute(
            select(func.count(PlaceModel.id)).where(PlaceModel.project_id == project_id)
        )
        return result.scalar_one()

    async def create(self, data: CreatePlaceData) -> Place:
        model = PlaceModel(
            project_id=data.project_id,
            external_id=data.external_id,
            title=data.title,
            artist_display=data.artist_display,
            image_url=data.image_url,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def update(self, place_id: int, delta: dict[str, Any]) -> Place:
        result = await self._session.execute(select(PlaceModel).where(PlaceModel.id == place_id))
        model = result.scalars().one()
        for key, value in delta.items():
            setattr(model, key, value)
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_domain(model)
