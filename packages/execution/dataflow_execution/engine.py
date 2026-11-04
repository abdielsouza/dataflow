"""Motor de execução da análise a partir de um grafo de operações."""


from dataflow_analytics import ChartEngine, PolarsEngine
from dataflow_domain import (
    Analysis,
    Artifact,
    ArtifactType,
    CreateChartOperation,
    Execution,
    ExecutionStatus,
    Operation,
)
from dataflow_storage import DatasetLoader
from hyperway import Unit

# from .context import ExecutionContext
from .executors import ExecutionStrategy, SequentialStageExecutor
from .planner import ExecutionPlanner, HyperwayExecutionGraph


class ExecutionEngine:
    """Orquestra a execução de uma análise e coleta os artefatos resultantes."""

    def __init__(
        self,
        dataset_loader: DatasetLoader | None = None,
        analytics_engine: PolarsEngine | None = None,
        chart_engine: ChartEngine | None = None,
        strategy: ExecutionStrategy | None = None,
    ) -> None:
        """Inicializa dependências de carregamento, análise e renderização de gráficos."""
        self._dataset_loader = dataset_loader or DatasetLoader()
        self._analytics_engine = analytics_engine or PolarsEngine()
        self._chart_engine = chart_engine or ChartEngine()
        self._strategy = strategy or SequentialStageExecutor()
        self._planner = ExecutionPlanner()

    def run(self, analysis: Analysis) -> Execution:
        """Executa a análise em ordem topológica e retorna um registro de execução."""
        execution = Execution(
            analysis_id=analysis.id,
            status=ExecutionStatus.RUNNING,
        )

        try:
            dataframe = self._dataset_loader.load(analysis.dataset.source)
            initial_artifact = Artifact(
                type=ArtifactType.TABLE,
                data=dataframe,
            )

            execution_graph = self._planner.build(analysis, self._execute_operation)
            stages = self._planner.plan_stages(execution_graph)

            for stage in stages:
                self._execute_stage(execution, initial_artifact, execution_graph, stage)

            execution.status = ExecutionStatus.COMPLETED

        except Exception as err:
            execution.status = ExecutionStatus.FAILED
            execution.error = str(err)

        return execution

    def _execute_operation(self, operation: Operation, inputs: tuple[Artifact, ...]) -> Artifact:
        """Dispara a operação correta com base em seu tipo."""
        if isinstance(operation, CreateChartOperation):
            if len(inputs) != 1:
                raise ValueError(f"'{CreateChartOperation.__name__}' requires exactly one input.")
    
            artifact = inputs[0]

            return self._chart_engine.create(operation.chart, artifact.data)

        return self._analytics_engine.execute(inputs, operation)

    def _execute_stage(
        self,
        execution: Execution,
        initial_artifact: Artifact,
        execution_graph: HyperwayExecutionGraph,
        nodes: tuple[Unit, ...],
    ) -> None:
        """Executa um estágio completo de nós e persiste os artefatos resultantes."""

        def execute_node(unit: Unit) -> Artifact:
            """Resolve upstream artifacts and runs the operation attached to a unit."""
            inputs = tuple(
                initial_artifact
                if connection.a is execution_graph.source
                else execution.artifacts_by_node[
                    execution_graph.operation_nodes[connection.a].id
                ]
                for connection in unit.get_inbound_connections(execution_graph.graph) or ()
            )
            return unit.func(*inputs)

        results = self._strategy.execute(nodes, execute_node)

        for unit, artifact in results.items():
            operation_node = execution_graph.operation_nodes[unit]
            execution.artifacts_by_node[operation_node.id] = artifact