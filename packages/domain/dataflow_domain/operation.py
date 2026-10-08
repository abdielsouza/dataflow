"""Abstrações base para operações do domínio analítico."""

from abc import ABC, abstractmethod


class Operation(ABC):
    """Representa uma transformação de dados executável por um motor analítico."""

    @property
    @abstractmethod
    def type(self) -> str:
        """Retorna o identificador da operação no sistema de domínio."""
        ...
