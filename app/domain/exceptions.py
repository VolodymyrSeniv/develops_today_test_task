class DomainError(Exception):
    pass


class ProjectNotFound(DomainError):
    pass


class PlaceNotFound(DomainError):
    pass


class PlaceLimitExceeded(DomainError):
    pass


class DuplicatePlace(DomainError):
    pass


class ArtworkNotFound(DomainError):
    pass


class ProjectHasVisitedPlaces(DomainError):
    pass
