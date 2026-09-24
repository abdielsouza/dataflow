import polars as pl
from typing import cast

from dataflow_analytics import PolarsEngine
from dataflow_domain import Analysis, Execution, ExecutionStatus


class ExecutionEngine:
    def __init__(self) -> None:
        self._analytics_engine = PolarsEngine()

    def run(self, analysis: Analysis, dataframe: pl.DataFrame) -> Execution:
        execution = Execution(analysis_id=analysis.id)
        execution.status = ExecutionStatus.RUNNING

        current_dataframe = dataframe

        for operation in analysis.operations:
            artifact = self._analytics_engine.execute(current_dataframe, operation)

            execution.artifacts.append(artifact)
            current_dataframe = cast(pl.DataFrame, artifact.data)

        execution.status = ExecutionStatus.COMPLETED

        return execution