from dataclasses import dataclass

from ..operation import Operation


@dataclass(frozen=True)
class ConcatOperation(Operation):
    @property
    def type(self) -> str:
        """Retorna o identificador estático da operação."""
        return "concat"