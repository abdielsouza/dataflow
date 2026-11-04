from typing import Protocol
from uuid import UUID

from ..user import User


class UserRepository(Protocol):
    def get_by_id(self, user_id: UUID) -> User | None:
        ...

    def get_by_email(self, email: str) -> User | None:
        ...

    def save(self, user: User) -> None:
        ...