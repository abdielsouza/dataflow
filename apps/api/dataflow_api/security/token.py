from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt


class TokenHandler:
    def __init__(self, secret_key: str, expires_in: timedelta = timedelta(minutes=30)) -> None:
        if len(secret_key.encode("utf-8")) < 32:
            raise ValueError("JWT secret must contain at least 32 bytes.")

        self._secret_key = secret_key
        self._expires_in = expires_in


    def create_access_token(self, user_id: UUID) -> str:
        now = datetime.now(timezone.utc)

        payload = {
            "sub": str(user_id),
            "iat": now,
            "exp": now + self._expires_in,
        }

        return jwt.encode(payload, self._secret_key, algorithm="HS256")


    def verify_access_token(self, token: str) -> UUID:
        payload = jwt.decode(
            token,
            self._secret_key,
            algorithms=["HS256"],
            options={"require": ["sub", "iat", "exp"]},
        )

        return UUID(payload["sub"])