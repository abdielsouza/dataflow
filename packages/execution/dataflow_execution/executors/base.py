from collections.abc import Callable
from abc import ABC, abstractmethod

from dataflow_domain import OperationNode, Artifact


class ExecutionStrategy(ABC):
    """Define a estratégia de execução de um estágio do grafo analítico."""

    @abstractmethod
    def execute(
        self,
        nodes: tuple[OperationNode, ...],
        execute_node: Callable[[OperationNode], Artifact]
    ) -> dict[OperationNode, Artifact]:
        """Executa um conjunto de nós e retorna os artefatos produzidos."""
        ...