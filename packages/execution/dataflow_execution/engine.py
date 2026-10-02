import polars as pl
from typing import cast, Optional

from dataflow_analytics import PolarsEngine
from dataflow_domain import (
    Analysis,
    Execution,
    ExecutionStatus,
    Artifact,
    ArtifactType,
)
from dataflow_storage import DatasetLoader


class ExecutionEngine:
    def __init__(
        self,
        dataset_loader: Optional[DatasetLoader] = None,
        analytics_engine: Optional[PolarsEngine] = None,
    ) -> None:
        self._dataset_loader = dataset_loader or DatasetLoader()
        self._analytics_engine = analytics_engine or PolarsEngine()

    def run(self, analysis: Analysis) -> Execution:
        execution = Execution(
            analysis_id=analysis.id,
            status=ExecutionStatus.RUNNING,
        )

        try:
            dataframe = self._dataset_loader.load(analysis.dataset.source)
            current_artifact = Artifact(
                type=ArtifactType.TABLE,
                data=dataframe,
            )

            for operation in analysis.operations:
                current_artifact = (
                    self._analytics_engine.execute(
                        current_artifact,
                        operation,
                    )
                )

                execution.artifacts.append(current_artifact)

            execution.status = ExecutionStatus.COMPLETED
        
        except Exception as err:
            execution.status = ExecutionStatus.FAILED
            execution.error = str(err)

        return execution
