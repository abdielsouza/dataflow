"""Planejamento da ordem de execução de operações em um grafo."""

from dataflow_domain import OperationNode, OperationGraph


class ExecutionPlanner:
    """Ordena os nós do grafo em uma sequência executável usando topological sort."""

    def plan(self, graph: OperationGraph) -> tuple[OperationNode, ...]:
        """Retorna a sequência topológica das operações do grafo."""
        return tuple(node for stage in self._plan_stages(graph) for node in stage)

    def _plan_stages(self, graph: OperationGraph) -> tuple[tuple[OperationNode, ...], ...]:
        nodes = graph.nodes
        
        in_degree = {node.id: len(graph.predecessors(node)) for node in nodes}
        ready = [node for node in nodes if in_degree[node.id] == 0]

        processed: set = set()
        stages: list[tuple[OperationNode, ...]] = []

        while ready:
            current_stage = tuple(ready)
            stages.append(current_stage)

            for node in current_stage:
                processed.add(node.id)

                for successor in graph.successors(node):
                    in_degree[successor.id] -= 1

            ready = [
                node for node in nodes
                if (node.id not in processed and in_degree[node.id] == 0)
            ]

        processed_nodes = sum(len(stage) for stage in stages)

        if processed_nodes != len(nodes):
            raise ValueError("Operation graph contains a cycle.")

        return tuple(stages)