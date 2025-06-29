from enum import StrEnum


class SortOption(StrEnum):
    asc: str = "imdb_rating"
    desc: str = "-imdb_rating"


class PermissionEnum(StrEnum):
    READ: str = "READ"
    CREATE: str = "CREATE"
    UPDATE: str = "UPDATE"
    DELETE: str = "DELETE"
