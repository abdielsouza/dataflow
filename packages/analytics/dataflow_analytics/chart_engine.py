"""Módulo responsável por encapsular especificações de gráficos em artefatos."""

from dataflow_domain import (
    Artifact,
    ArtifactType,
    ChartSpec,
)

import polars as pl


class ChartEngine:
    """Cria artefatos de saída para gráficos definidos por especificações de domínio."""

    def create(self, chart: ChartSpec, dataframe: pl.DataFrame) -> Artifact:
        """Retorna um artefato de gráfico com a especificação e os dados associados."""
        return Artifact(
            type=ArtifactType.CHART,
            data={
                "spec": chart,
                "data": dataframe,
            },
        )
