"""Definições de análise e grafo de operações do domínio."""

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from .dataset import Dataset
from .graph import OperationGraph, OperationNode
from .operation import Operation


@dataclass
class Analysis:
    """Agrupa um conjunto de operações aplicadas a um dataset específico."""

    name: str
    dataset: Dataset
    id: UUID = field(default_factory=uuid4)
    graph: OperationGraph = field(default_factory=OperationGraph)

    def add_operation(self, operation: Operation) -> OperationNode:
        """Insere uma nova operação no grafo e retorna o nó correspondente."""
        return self.graph.add_node(operation)
