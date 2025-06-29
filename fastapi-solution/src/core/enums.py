from enum import StrEnum


class PermissionEnum(StrEnum):
    READ: str = "READ"
    CREATE: str = "CREATE"
    UPDATE: str = "UPDATE"
    DELETE: str = "DELETE"
