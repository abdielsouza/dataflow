"""Operação de ordenação de registros em tabelas."""

from dataclasses import dataclass

from ..operation import Operation


@dataclass(frozen=True)
class SortOperation(Operation):
    """Ordena uma tabela por uma sequência de colunas, em ordem ascendente ou descendente."""

    columns: tuple[str, ...]
    descending: bool = False

    @property
    def type(self) -> str:
        """Retorna o identificador estático da operação."""
        return "sort"
