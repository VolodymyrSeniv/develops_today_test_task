from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ArtworkData:
    id: int
    title: str
    artist_display: str | None
    image_url: str | None


class AbstractArtworkService(ABC):
    @abstractmethod
    async def get_artwork(self, artwork_id: int) -> ArtworkData | None: ...
