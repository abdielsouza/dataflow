from dataclasses import dataclass

from ..operation import Operation


@dataclass(frozen=True)
class GroupByOperation(Operation):
    columns: tuple[str, ...]
    aggregations: dict[str, str]

    @property
    def type(self) -> str:
        return "group_by"
