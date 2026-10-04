"""Estruturas de grafo para encadear operações de análise."""

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from .operation import Operation


@dataclass
class OperationNode:
    """Representa um nó do grafo contendo uma operação e um identificador único."""

    operation: Operation
    id: UUID = field(default_factory=uuid4)

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, OperationNode):
            return NotImplemented

        return self.id == other.id


@dataclass(frozen=True)
class OperationEdge:
    """Conecta uma operação origem e uma operação destino."""

    source: UUID
    target: UUID

    def __hash__(self):
        return hash((self.source, self.target))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, OperationEdge):
            return NotImplemented

        return (self.source == other.source) and (self.target == other.target)

class OperationGraph:
    """Armazena operações e as dependências entre elas em um grafo acíclico."""

    def __init__(self) -> None:
        self._nodes: dict[UUID, OperationNode] = {}
        self._edges: list[OperationEdge] = []

    @property
    def nodes(self) -> tuple[OperationNode, ...]:
        """Retorna as operações contidas no grafo."""
        return tuple(self._nodes.values())

    @property
    def edges(self) -> tuple[OperationEdge, ...]:
        """Retorna as arestas que representam dependências entre operações."""
        return tuple(self._edges)

    def add_node(self, operation: Operation) -> OperationNode:
        """Adiciona um novo nó ao grafo e retorna o objeto criado."""
        node = OperationNode(operation)
        self._nodes[node.id] = node

        return node

    def add_edge(self, source: OperationNode, target: OperationNode) -> None:
        """Cria uma dependência entre dois nós pertencentes a este grafo."""
        if source.id not in self._nodes:
            raise ValueError("Source node does not belong to graph.")

        if target.id not in self._nodes:
            raise ValueError("Target node does not belong to graph.")

        self._edges.append(OperationEdge(source.id, target.id))

    def predecessors(self, node: OperationNode) -> tuple[OperationNode, ...]:
        """Retorna os nós que alimentam diretamente o nó informado."""
        predecessor_ids = {edge.source for edge in self._edges if edge.target == node.id}

        return tuple(self._nodes[node_id] for node_id in predecessor_ids)

    def successors(self, node: OperationNode) -> tuple[OperationNode, ...]:
        """Retorna os nós diretamente dependentes do nó informado."""
        successor_ids = {edge.target for edge in self._edges if edge.source == node.id}

        return tuple(self._nodes[node_id] for node_id in successor_ids)
