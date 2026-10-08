"""Base para roteadores da API com registro automático de endpoints."""

from abc import ABC, abstractmethod
from typing import ClassVar

from fastapi import APIRouter, FastAPI


class AbstractRouter(ABC):
    """Define o contrato mínimo para roteadores que expõem endpoints FastAPI."""

    prefix: ClassVar[str]
    tags: ClassVar[tuple[str, ...]]

    def __init__(self) -> None:
        """Inicializa o roteador interno e registra as rotas do sub-roteador."""
        self._router = APIRouter(
            prefix=self.prefix,
            tags=list(self.tags),
        )

        self._register_routes()

    @property
    def router(self) -> APIRouter:
        """Retorna o roteador FastAPI configurado com as rotas deste módulo."""
        return self._router

    @abstractmethod
    def _register_routes(self):
        """Registra as rotas concretas implementadas por cada subclasse."""
        ...

    def include_in(self, app: FastAPI) -> None:
        """Inclui este roteador na aplicação principal."""
        app.include_router(self._router)