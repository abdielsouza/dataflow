from pydantic import BaseModel
from uuid import UUID

from dataflow_domain import User


class RegisterRequest(BaseModel):
    username:   str
    email:      str
    password:   str


class LoginRequest(BaseModel):
    email:      str
    password:   str


class UserResponse(BaseModel):
    id:         UUID
    username:   str
    email:      str

    @classmethod
    def from_domain(cls, user: User) -> UserResponse:
        return cls(
            id=user.id,
            username=user.username,
            email=user.email,
        )


class TokenResponse(BaseModel):
    access_token:   str
    token_type:     str = "bearer"