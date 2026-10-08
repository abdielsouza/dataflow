"""Motor de execução da análise a partir de um grafo de operações."""

from typing import Optional

from dataflow_analytics import PolarsEngine, ChartEngine
from dataflow_domain import (
    Analysis,
    Execution,
    ExecutionStatus,
    Artifact,
    ArtifactType,
    CreateChartOperation,
    Operation,
    OperationNode,
)
from dataflow_storage import DatasetLoader
from .planner import ExecutionPlanner
# from .context import ExecutionContext
from .executors import SequentialStageExecutor, ExecutionStrategy


class ExecutionEngine:
    """Orquestra a execução de uma análise e coleta os artefatos resultantes."""

    def __init__(
        self,
        dataset_loader: Optional[DatasetLoader] = None,
        analytics_engine: Optional[PolarsEngine] = None,
        chart_engine: Optional[ChartEngine] = None,
        strategy: Optional[ExecutionStrategy] = None,
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

            plan = self._planner.plan(analysis.graph)

            for node in plan:
                predecessors = analysis.graph.predecessors(node)

                inputs = self._resolve_inputs(execution, initial_artifact, predecessors)
                artifact = self._execute_operation(node.operation, inputs)

                execution.artifacts_by_node[node.id] = artifact

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

    def _resolve_inputs(
        self,
        execution: Execution,
        initial_artifact: Artifact,
        predecessors: tuple[OperationNode, ...],
    ) -> tuple[Artifact, ...]:
        """Obtém o artefato produzido pelo predecessor único da operação atual."""
        if not predecessors:
            return tuple([initial_artifact])

        return tuple(execution.artifacts_by_node[node.id] for node in predecessors)

    def _execute_stage(
        self,
        execution: Execution,
        initial_artifact: Artifact,
        nodes: tuple[OperationNode, ...],
    ) -> None:
        """Executa um estágio completo de nós e persiste os artefatos resultantes."""

        def execute_node(node: OperationNode) -> Artifact:
            """Resolve os dados de entrada para um nó e executa a operação correspondente."""
            inputs = self._resolve_inputs(execution, initial_artifact, tuple([node]))
            return self._execute_operation(node.operation, inputs)

        results = self._strategy.execute(nodes, execute_node)

        for node, artifact in results.items():
            execution.artifacts_by_node[node.id] = artifact