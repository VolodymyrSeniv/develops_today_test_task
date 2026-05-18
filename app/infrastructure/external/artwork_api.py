import time
from typing import Any

import httpx
from loguru import logger

from app.application.ports.artwork_service import AbstractArtworkService, ArtworkData
from app.infrastructure.config import get_settings

settings = get_settings()

_FIELDS = "id,title,artist_display,image_id"

_cache: dict[int, tuple[ArtworkData, float]] = {}


class ArtworkApiService(AbstractArtworkService):
    async def get_artwork(self, artwork_id: int) -> ArtworkData | None:
        now = time.monotonic()
        cached = _cache.get(artwork_id)
        if cached is not None:
            data, expires_at = cached
            if now < expires_at:
                logger.debug("Artwork {} served from cache", artwork_id)
                return data

        url = f"{settings.artwork_api_base_url}/artworks/{artwork_id}"
        logger.debug("Fetching artwork {} from Art Institute API", artwork_id)
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params={"fields": _FIELDS})

            if response.status_code == 404:
                logger.warning("Artwork {} not found in Art Institute API", artwork_id)
                return None

            response.raise_for_status()
            raw: dict[str, Any] = response.json().get("data") or {}
        except httpx.HTTPError as exc:
            logger.error("HTTP error fetching artwork {}: {}", artwork_id, exc)
            return None

        image_id: str | None = raw.get("image_id")
        image_url = (
            f"https://www.artic.edu/iiif/2/{image_id}/full/400,/0/default.jpg" if image_id else None
        )

        artwork = ArtworkData(
            id=raw["id"],
            title=raw.get("title") or "Untitled",
            artist_display=raw.get("artist_display"),
            image_url=image_url,
        )
        _cache[artwork_id] = (artwork, now + settings.artwork_cache_ttl)
        logger.debug("Artwork {} cached (ttl={}s)", artwork_id, settings.artwork_cache_ttl)
        return artwork
