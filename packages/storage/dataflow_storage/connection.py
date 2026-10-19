import turso_serverless
from dotenv import load_dotenv

from .config import TursoConfig


def connect_database():
    load_dotenv()
    config = TursoConfig.from_env()

    return turso_serverless.connect(
        config.database_url,
        auth_token=config.auth_token,
    )