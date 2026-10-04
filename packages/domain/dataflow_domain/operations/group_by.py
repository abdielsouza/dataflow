"""Operação de agrupamento e agregação de registros."""

from dataclasses import dataclass

from ..operation import Operation


@dataclass(frozen=True)
class GroupByOperation(Operation):
    """Agrupa registros por uma ou mais colunas e aplica agregações."""

    columns: tuple[str, ...]
    aggregations: dict[str, str]

    @property
    def type(self) -> str:
        """Retorna o identificador estático da operação."""
        return "group_by"
