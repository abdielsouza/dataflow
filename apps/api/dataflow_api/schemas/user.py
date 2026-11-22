from uuid import UUID

from pydantic import BaseModel
from dataflow_domain import User


class UpdateUserRequest(BaseModel):
    username: str | None = None
    email: str | None = None
    password: str | None = None


class UpdateUserResponse(BaseModel):
    id: UUID
    username: str
    email: str

    @classmethod
    def from_domain(cls, user: User) -> "UpdateUserResponse":
        return cls(id=user.id, username=user.username, email=user.email)
