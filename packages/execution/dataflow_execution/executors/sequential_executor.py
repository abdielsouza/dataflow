from .base import ExecutionStrategy


class SequentialStageExecutor(ExecutionStrategy):
    """Executa um estágio de operações em ordem sequencial."""

    def execute(self, nodes, execute_node):
        """Processa cada nó do estágio na ordem em que foi recebido."""
        if not nodes:
            return {}

        result = {
            node: execute_node(node) for node in nodes
        }

        return result