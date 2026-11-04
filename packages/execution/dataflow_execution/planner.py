"""Build and plan Dataflow execution graphs using Hyperway."""

from collections.abc import Callable
from dataclasses import dataclass
from uuid import UUID

from dataflow_domain import Analysis, Artifact, Operation, OperationNode
from hyperway import Graph, Unit


@dataclass(frozen=True)
class HyperwayExecutionGraph:
    graph: Graph
    source: Unit
    units: tuple[Unit, ...]
    operation_nodes: dict[Unit, OperationNode]


class ExecutionPlanner:
    """Translate domain analyses to Hyperway and order their execution stages."""

    def build(
        self,
        analysis: Analysis,
        execute_operation: Callable[[Operation, tuple[Artifact, ...]], Artifact],
    ) -> HyperwayExecutionGraph:
        """Create Hyperway units and connections for an analysis."""
        graph = Graph()
        source = Unit(lambda artifact: artifact, name="dataset")
        units_by_id: dict[UUID, Unit] = {}
        operation_nodes: dict[Unit, OperationNode] = {}

        for node in analysis.graph.nodes:
            unit = Unit(
                lambda *inputs, operation=node.operation: execute_operation(
                    operation,
                    tuple(inputs),
                ),
                name=f"operation-{node.id}",
            )
            units_by_id[node.id] = unit
            operation_nodes[unit] = node

        incoming_ids = {edge.target for edge in analysis.graph.edges}
        for edge in analysis.graph.edges:
            graph.add(units_by_id[edge.source], units_by_id[edge.target])

        for node in analysis.graph.nodes:
            if node.id not in incoming_ids:
                graph.add(source, units_by_id[node.id])

        return HyperwayExecutionGraph(
            graph=graph,
            source=source,
            units=tuple(operation_nodes),
            operation_nodes=operation_nodes,
        )

    def plan(self, execution_graph: HyperwayExecutionGraph) -> tuple[Unit, ...]:
        """Return Hyperway units in topological order."""
        return tuple(unit for stage in self.plan_stages(execution_graph) for unit in stage)

    def plan_stages(
        self,
        execution_graph: HyperwayExecutionGraph,
    ) -> tuple[tuple[Unit, ...], ...]:
        """Return batches of Hyperway units whose dependencies are satisfied."""
        units = (execution_graph.source, *execution_graph.units)
        graph = execution_graph.graph
        in_degree = {
            unit: len(unit.get_inbound_connections(graph) or ())
            for unit in units
        }
        ready = [unit for unit in units if in_degree[unit] == 0]

        processed: set[Unit] = set()
        stages: list[tuple[Unit, ...]] = []

        while ready:
            current_stage = tuple(ready)
            operation_stage = tuple(
                unit for unit in current_stage if unit is not execution_graph.source
            )
            if operation_stage:
                stages.append(operation_stage)

            for unit in current_stage:
                processed.add(unit)

                for connection in unit.get_outbound_connections(graph) or ():
                    in_degree[connection.b] -= 1

            ready = [
                unit for unit in units
                if unit not in processed and in_degree[unit] == 0
            ]

        if len(processed) != len(units):
            raise ValueError("Execution graph contains a cycle.")

        return tuple(stages)