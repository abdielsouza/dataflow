from concurrent.futures import ThreadPoolExecutor
from typing import Optional

from .base import ExecutionStrategy


class ConcurrentStageExecutor(ExecutionStrategy):
    def __init__(self, max_workers: Optional[int] = None) -> None:
        self._max_workers = max_workers or 2

    def execute(self, nodes, execute_node):
        if not nodes:
            return {}
        
        with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
            futures = {
                node: executor.submit(execute_node, node) for node in nodes
            }

            results = {node: future.result() for node, future in futures.items()}

            return results