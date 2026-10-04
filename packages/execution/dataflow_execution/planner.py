"""Planejamento da ordem de execução de operações em um grafo."""

from dataflow_domain import OperationNode, OperationGraph


class ExecutionPlanner:
    """Ordena os nós do grafo em uma sequência executável usando topological sort."""

    def plan(self, graph: OperationGraph) -> tuple[OperationNode, ...]:
        """Retorna a sequência topológica das operações do grafo."""
        nodes = graph.nodes

        in_degree = {node.id: len(graph.predecessors(node)) for node in nodes}
        ready = [node for node in nodes if in_degree[node.id] == 0]

        ordered: list[OperationNode] = []

        while ready:
            node = ready.pop(0)
            ordered.append(node)

            for successor in graph.successors(node):
                in_degree[successor.id] -= 1

                if in_degree[successor.id] == 0:
                    ready.append(successor)

        if len(ordered) != len(nodes):
            raise ValueError("Operation graph contains a cycle.")

        return tuple(ordered)
