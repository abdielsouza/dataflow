from dataclasses import dataclass, field
from uuid import UUID, uuid4

from .operation import Operation
from .dataset import Dataset


@dataclass
class Analysis:
    name: str
    dataset: Dataset
    id: UUID = field(default_factory=uuid4)
    operations: list[Operation] = field(default_factory=list)

    def add_operation(self, operation: Operation) -> None:
        self.operations.append(operation)
