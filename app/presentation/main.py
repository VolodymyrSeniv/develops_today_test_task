import time
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.infrastructure.config import get_settings
from app.infrastructure.logging import setup_logging
from app.presentation.api.v1.places.router import router as places_router
from app.presentation.api.v1.projects.router import router as projects_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    setup_logging()
    logger.info("Starting {} v{}", settings.app_name, settings.app_version)
    yield
    logger.info("Shutting down {}", settings.app_name)
    await logger.complete()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Travel Planner API — manage travel projects and artwork-based places to visit.\n\n"
        "Artwork data is sourced from the [Art Institute of Chicago API](https://api.artic.edu/docs/)."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start
    logger.info(
        "{} {} {} {:.3f}s",
        request.method,
        request.url.path,
        response.status_code,
        duration,
    )
    return response


API_PREFIX = "/api/v1"
app.include_router(projects_router, prefix=API_PREFIX)
app.include_router(places_router, prefix=API_PREFIX)


@app.get("/health", tags=["Health"], summary="Health check")
async def health_check() -> dict[str, str]:
    return {"status": "ok", "version": settings.app_version}
