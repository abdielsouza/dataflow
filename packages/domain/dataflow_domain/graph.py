from dataclasses import dataclass, field
from uuid import UUID, uuid4

from .operation import Operation


@dataclass
class OperationNode:
    operation:  Operation
    id:         UUID = field(default_factory=uuid4)

@dataclass(frozen=True)
class OperationEdge:
    source: UUID
    target: UUID

class OperationGraph:
    def __init__(self) -> None:
        self._nodes: dict[UUID, OperationNode] = {}
        self._edges: list[OperationEdge] = []

    @property
    def nodes(self) -> tuple[OperationNode, ...]:
        return tuple(self._nodes.values())

    @property
    def edges(self) -> tuple[OperationEdge, ...]:
        return tuple(self._edges)

    def add_node(self, operation: Operation) -> OperationNode:
        node = OperationNode(operation)
        self._nodes[node.id] = node

        return node

    def add_edge(self, source: OperationNode, target: OperationNode) -> None:
        if source.id not in self._nodes:
            raise ValueError("Source node does not belong to graph.")

        if target.id not in self._nodes:
            raise ValueError("Target node does not belong to graph.")

        self._edges.append(OperationEdge(source.id, target.id))
    
    def predecessors(self, node: OperationNode) -> tuple[OperationNode, ...]:
        predecessor_ids = {edge.source for edge in self._edges if edge.target == node.id}

        return tuple(self._nodes[node_id] for node_id in predecessor_ids)

    def successors(self, node: OperationNode) -> tuple[OperationNode, ...]:
        successor_ids = {edge.target for edge in self._edges if edge.source == node.id}

        return tuple(self._nodes[node_id] for node_id in successor_ids)