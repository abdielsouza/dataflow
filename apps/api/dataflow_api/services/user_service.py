from uuid import UUID

from dataflow_domain import User, UserRepository

from ..security import PasswordHandler


class UserService:
    def __init__(
        self,
        repo: UserRepository,
        password_handler: PasswordHandler | None = None,
    ) -> None:
        self._repo = repo
        self._password_handler = password_handler

    def get_user(self, user_id: UUID) -> User | None:
        return self._repo.get_by_id(user_id)

    def delete_user(self, user_id: UUID) -> None:
        self._repo.delete(user_id)

    def update_user(
        self,
        user_id: UUID,
        username: str | None = None,
        email: str | None = None,
        password: str | None = None,
    ) -> User:
        user = self._repo.get_by_id(user_id)
        if user is None:
            raise LookupError("User not found.")

        if username is not None:
            username = username.strip()
            if not username:
                raise ValueError("Username must not be empty.")
            user.username = username

        if email is not None:
            email = email.strip().casefold()
            if not email:
                raise ValueError("Email must not be empty.")
            existing = self._repo.get_by_email(email)
            if existing is not None and existing.id != user.id:
                raise ValueError("User with this email already exists.")
            user.email = email

        if password is not None:
            if not password:
                raise ValueError("Password must not be empty.")
            if self._password_handler is None:
                raise RuntimeError("PasswordHandler is required to update passwords.")
            user.password = self._password_handler.hash(password)

        self._repo.update(user)
        return user
