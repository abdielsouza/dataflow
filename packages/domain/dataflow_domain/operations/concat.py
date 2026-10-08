"""Operação de concatenação de múltiplas tabelas."""

from dataclasses import dataclass

from ..operation import Operation


@dataclass(frozen=True)
class ConcatOperation(Operation):
    """Combina dois ou mais artefatos tabulares em uma única tabela."""

    @property
    def type(self) -> str:
        """Retorna o identificador estático da operação."""
        return "concat"