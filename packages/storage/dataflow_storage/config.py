import os
from dataclasses import dataclass


@dataclass(frozen=True)
class TursoConfig:
    database_url: str
    auth_token: str

    @classmethod
    def from_env(cls) -> "TursoConfig":
        database_url = os.getenv("TURSO_DATABASE_URL")
        auth_token = os.getenv("TURSO_AUTH_TOKEN")

        if not database_url or not auth_token:
            raise RuntimeError(
                "TURSO_DATABASE_URL and TURSO_AUTH_TOKEN "
                "must be configured."
            )

        return cls(
            database_url=database_url,
            auth_token=auth_token,
        )