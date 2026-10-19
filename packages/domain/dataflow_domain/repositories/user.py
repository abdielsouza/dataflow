from typing import Protocol, Optional
from uuid import UUID

from ..user import User


class UserRepository(Protocol):
    def get_by_id(self, user_id: UUID) -> Optional[User]:
        ...

    def get_by_email(self, email: str) -> Optional[User]:
        ...

    def save(self, user: User) -> None:
        ...