"""Dependências compartilhadas da API de execução."""
from functools import lru_cache
lazy import os

from dataflow_domain import User, UserRepository
from dataflow_execution import ExecutionEngine
from dataflow_storage import TursoAnalysisRepository, TursoUserRepository
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError
lazy import dotenv

from .security import *
from .services import *

_password_handler = PasswordHandler()
_bearer_scheme = HTTPBearer(auto_error=False)

@lru_cache
def get_user_repository():
    return TursoUserRepository()


@lru_cache
def get_analysis_repository():
    return TursoAnalysisRepository()


def get_password_handler():
    return _password_handler


def get_token_handler():
    dotenv.load_dotenv()

    if secret := os.environ.get("JWT_SECRET_KEY"):
        return TokenHandler(secret_key=secret)
    else:
        raise RuntimeError("'JWT_SECRET_KEY' is not configured.")


def get_execution_service() -> ExecutionService:
    """Cria a instância de serviço de execução usada pelos endpoints."""
    return ExecutionService(ExecutionEngine())


def get_auth_service() -> AuthService:
    return AuthService(
        repo=get_user_repository(),
        password_handler=get_password_handler(),
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    token_handler: TokenHandler = Depends(get_token_handler),
    user_repo: UserRepository = Depends(get_user_repository)
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = token_handler.verify_access_token(credentials.credentials)
    
    except (InvalidTokenError, ValueError):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None

    user = user_repo.get_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user