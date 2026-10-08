from concurrent.futures import ThreadPoolExecutor
from typing import Optional

from .base import ExecutionStrategy


class ConcurrentStageExecutor(ExecutionStrategy):
    """Executa um estágio de operações em paralelo usando threads."""

    def __init__(self, max_workers: Optional[int] = None) -> None:
        """Configura o número máximo de workers usados em paralelo."""
        self._max_workers = max_workers or 2

    def execute(self, nodes, execute_node):
        """Executa cada nó em paralelo e devolve os resultados por identificador."""
        if not nodes:
            return {}

        with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
            futures = {
                node: executor.submit(execute_node, node) for node in nodes
            }

            results = {node: future.result() for node, future in futures.items()}

            return results