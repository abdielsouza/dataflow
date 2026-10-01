from dataflow_domain import (
    Artifact, 
    ArtifactType, 
    ChartSpec,
)

import polars as pl


class ChartEngine:
    def create(self, chart: ChartSpec, dataframe: pl.DataFrame) -> Artifact:
        return Artifact(
            type=ArtifactType.CHART,
            data={
                "spec": chart,
                "data": dataframe,
            },
        )