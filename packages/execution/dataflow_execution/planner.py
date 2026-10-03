from dataflow_domain import OperationNode, OperationGraph


class ExecutionPlanner:
    def plan(self, graph: OperationGraph) -> tuple[OperationNode, ...]:
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