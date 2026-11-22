from uuid import UUID

from dataflow_domain import User


class InMemoryUserRepository:
    def __init__(self) -> None:
        self._users_by_id: dict[UUID, User] = {}
        self._user_ids_by_email: dict[str, UUID] = {}

    def get_by_id(self, user_id: UUID) -> User | None:
        return self._users_by_id.get(user_id)

    def get_by_email(self, email: str) -> User | None:
        user_id = self._user_ids_by_email.get(email)

        return None if user_id is None else self._users_by_id[user_id]

    def save(self, user: User) -> None:
        existing_id = self._user_ids_by_email.get(user.email)

        if existing_id is not None and existing_id != user.id:
            raise ValueError("User with this email already exists.")

        self._users_by_id[user.id] = user
        self._user_ids_by_email[user.email] = user.id

    def update(self, user: User) -> None:
        existing = self._users_by_id.get(user.id)
        if existing is not None:
            old_email = existing.email
            if old_email != user.email:
                self._user_ids_by_email.pop(old_email, None)

        existing_id = self._user_ids_by_email.get(user.email)
        if existing_id is not None and existing_id != user.id:
            raise ValueError("User with this email already exists.")

        self._users_by_id[user.id] = user
        self._user_ids_by_email[user.email] = user.id

    def delete(self, user_id: UUID) -> None:
        user = self._users_by_id.pop(user_id, None)
        if user is not None:
            if self._user_ids_by_email.get(user.email) == user_id:
                self._user_ids_by_email.pop(user.email, None)