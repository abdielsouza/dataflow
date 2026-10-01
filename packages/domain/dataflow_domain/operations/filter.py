from dataclasses import dataclass

from ..operation import Operation

@dataclass(frozen=True)
class FilterOperation(Operation):
    column:     str
    operator:   str
    value:      object

    @property
    def type(self) -> str:
        return "filter"
