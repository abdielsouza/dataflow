from abc import ABC, abstractmethod
from collections.abc import Callable

from dataflow_domain import Artifact
from hyperway import Unit


class ExecutionStrategy(ABC):
    """Define a estratégia de execução de um estágio do grafo analítico."""

    @abstractmethod
    def execute(
        self,
        nodes: tuple[Unit, ...],
        execute_node: Callable[[Unit], Artifact],
    ) -> dict[Unit, Artifact]:
        """Executa um conjunto de nós e retorna os artefatos produzidos."""
        ...