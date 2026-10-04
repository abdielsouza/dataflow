from .base import ExecutionStrategy


class SequentialStageExecutor(ExecutionStrategy):
    def execute(self, nodes, execute_node):
        if not nodes:
            return {}

        result = {
            node: execute_node(node) for node in nodes
        }

        return result