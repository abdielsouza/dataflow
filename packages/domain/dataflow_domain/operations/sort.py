from dataclasses import dataclass

from ..operation import Operation


@dataclass(frozen=True)
class SortOperation(Operation):
    columns:    tuple[str, ...]
    descending: bool = False

    @property
    def type(self) -> str:
        return "sort"