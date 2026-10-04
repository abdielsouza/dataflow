from collections.abc import Callable
from abc import ABC, abstractmethod

from dataflow_domain import OperationNode, Artifact


class ExecutionStrategy(ABC):
    @abstractmethod
    def execute(
        self,
        nodes: tuple[OperationNode, ...],
        execute_node: Callable[[OperationNode], Artifact]
    ) -> dict[OperationNode, Artifact]:
        ...