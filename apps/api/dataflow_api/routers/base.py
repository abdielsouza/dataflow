from abc import ABC, abstractmethod
from typing import ClassVar

from fastapi import APIRouter, FastAPI


class AbstractRouter(ABC):
    prefix: ClassVar[str]
    tags: ClassVar[tuple[str, ...]]

    def __init__(self) -> None:
        self._router = APIRouter(
            prefix=self.prefix,
            tags=list(self.tags),
        )

        self._register_routes()

    @property
    def router(self) -> APIRouter:
        return self._router

    @abstractmethod
    def _register_routes(self):
        ...

    def include_in(self, app: FastAPI) -> None:
        app.include_router(self._router)