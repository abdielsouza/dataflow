"""Motor de execução da análise a partir de um grafo de operações."""

import polars as pl
from typing import cast, Optional

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
from .context import ExecutionContext


class ExecutionEngine:
    """Orquestra a execução de uma análise e coleta os artefatos resultantes."""

    def __init__(
        self,
        dataset_loader: Optional[DatasetLoader] = None,
        analytics_engine: Optional[PolarsEngine] = None,
        chart_engine: Optional[ChartEngine] = None,
    ) -> None:
        """Inicializa dependências de carregamento, análise e renderização de gráficos."""
        self._dataset_loader = dataset_loader or DatasetLoader()
        self._analytics_engine = analytics_engine or PolarsEngine()
        self._chart_engine = chart_engine or ChartEngine()
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
            context = ExecutionContext()

            for node in plan:
                predecessors = analysis.graph.predecessors(node)

                if not predecessors:
                    input_artifact = initial_artifact
                else:
                    input_artifact = self._resolve_input(context, predecessors)

                artifact = self._execute_operation(node.operation, input_artifact)

                context.set_artifact(node.id, artifact)
                execution.artifacts_by_node[node.id] = artifact

            execution.status = ExecutionStatus.COMPLETED

        except Exception as err:
            execution.status = ExecutionStatus.FAILED
            execution.error = str(err)

        return execution

    def _execute_operation(self, operation: Operation, artifact: Artifact) -> Artifact:
        """Dispara a operação correta com base em seu tipo."""
        if isinstance(operation, CreateChartOperation):
            return self._chart_engine.create(operation.chart, artifact.data)

        return self._analytics_engine.execute(artifact, operation)

    def _resolve_input(
        self, context: ExecutionContext, predecessors: tuple[OperationNode, ...]
    ) -> Artifact:
        """Obtém o artefato produzido pelo predecessor único da operação atual."""
        if len(predecessors) != 1:
            raise ValueError("Operation currently requires exactly one input.")

        return context.get_artifact(predecessors[0].id)
