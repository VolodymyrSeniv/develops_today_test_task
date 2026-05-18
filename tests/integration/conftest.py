import asyncio
import os
from collections.abc import AsyncGenerator
from urllib.parse import urlparse

import asyncpg
import pytest
from dotenv import load_dotenv
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.application.ports.artwork_service import AbstractArtworkService, ArtworkData
from app.infrastructure.persistence.models import Base
from app.presentation.dependencies import get_artwork_service, get_db
from app.presentation.main import app

load_dotenv()

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5433/travel_planner_test",
)

KNOWN_ARTWORKS: dict[int, ArtworkData] = {
    1001: ArtworkData(id=1001, title="Nighthawks", artist_display="Edward Hopper", image_url=None),
    1002: ArtworkData(
        id=1002, title="American Gothic", artist_display="Grant Wood", image_url=None
    ),
    1003: ArtworkData(
        id=1003, title="The Bedroom", artist_display="Vincent van Gogh", image_url=None
    ),
    1004: ArtworkData(
        id=1004, title="The Old Guitarist", artist_display="Pablo Picasso", image_url=None
    ),
}


class FakeArtworkService(AbstractArtworkService):
    async def get_artwork(self, artwork_id: int) -> ArtworkData | None:
        return KNOWN_ARTWORKS.get(artwork_id)


async def _ensure_test_database() -> None:
    parsed = urlparse(TEST_DATABASE_URL.replace("postgresql+asyncpg", "postgresql"))
    dbname = parsed.path.lstrip("/")
    admin_dsn = TEST_DATABASE_URL.replace(f"/{dbname}", "/postgres").replace(
        "postgresql+asyncpg", "postgresql"
    )
    conn = await asyncpg.connect(dsn=admin_dsn)
    try:
        exists = await conn.fetchval("SELECT 1 FROM pg_database WHERE datname = $1", dbname)
        if not exists:
            await conn.execute(f'CREATE DATABASE "{dbname}"')
    finally:
        await conn.close()


def pytest_configure(config: pytest.Config) -> None:
    asyncio.run(_bootstrap())


async def _bootstrap() -> None:
    await _ensure_test_database()
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_artwork_service] = lambda: FakeArtworkService()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    async with session_factory() as session:
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(table.delete())
        await session.commit()

    await engine.dispose()
    app.dependency_overrides.clear()
