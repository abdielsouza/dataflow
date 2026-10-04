"""Operação de filtragem em colunas de dados tabulares."""

from dataclasses import dataclass

from ..operation import Operation


@dataclass(frozen=True)
class FilterOperation(Operation):
    """Aplica um filtro booleano a uma coluna de uma tabela."""

    column: str
    operator: str
    value: object

    @property
    def type(self) -> str:
        """Retorna o identificador estático da operação."""
        return "filter"
