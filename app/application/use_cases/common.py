from dataclasses import dataclass


@dataclass
class PagedResult[T]:
    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int
