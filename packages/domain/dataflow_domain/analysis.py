from dataclasses import dataclass, field
from uuid import UUID, uuid4

from .operation import Operation
from .dataset import Dataset
from .graph import OperationGraph, OperationNode


@dataclass
class Analysis:
    name: str
    dataset: Dataset
    id: UUID = field(default_factory=uuid4)
    graph: OperationGraph = field(default_factory=OperationGraph)

    def add_operation(self, operation: Operation) -> OperationNode:
        return self.graph.add_node(operation)
