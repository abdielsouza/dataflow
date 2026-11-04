from dataflow_domain import User, UserRepository

from ..security import PasswordHandler


class AuthService:
    def __init__(
        self,
        repo: UserRepository,
        password_handler: PasswordHandler,
    ) -> None:
        self._repo = repo
        self._password_handler = password_handler

    def register(self, username: str, email: str, password: str) -> User:
        normalized_email = email.strip().casefold()
        normalized_username = username.strip()

        if not normalized_username:
            raise ValueError("Username must not be empty.")
        
        if not normalized_email:
            raise ValueError("Email must not be empty.")

        if not password:
            raise ValueError("Password must not be empty.")

        if self._repo.get_by_email(normalized_email) is not None:
            raise ValueError("User with this email already exists.")

        user = User(
            username=normalized_username,
            email=normalized_email,
            password=self._password_handler.hash(password),
        )

        self._repo.save(user)

        return user

    def authenticate(self, email: str, password: str) -> User:
        normalized_email = email.strip().casefold()
        user = self._repo.get_by_email(normalized_email)

        if user is None or not self._password_handler.verify(user.password, password):
            raise ValueError("Invalid credentials.")

        return user