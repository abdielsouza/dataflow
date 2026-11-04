"""Renderizador de gráficos para o backend Plotly."""

import json
from typing import Any, cast

import plotly.graph_objects as go
import plotly.io as pio
import polars as pl
from dataflow_domain import Artifact, ArtifactType, ChartSpec, ChartType

from ..models import *


class PlotlyRenderer:
    """Converte artefatos de tipo gráfico em objetos Plotly serializáveis."""

    def render(self, artifact: Artifact) -> RenderedArtifact:
        """Gera um artefato renderizado a partir de um gráfico de domínio."""
        if artifact.type != ArtifactType.CHART:
            raise ValueError("PlotlyRenderer requires a chart artifact.")

        spec: ChartSpec = artifact.data["spec"]
        dataframe: pl.DataFrame = artifact.data["data"]

        figure = self._create_figure(dataframe, spec)
        parsed = cast(Any, pio.to_json(figure))

        return RenderedArtifact(
            type=RenderedArtifactType.CHART,
            renderer=RendererType.PLOTLY,
            data=json.loads(parsed),
            metadata={
                "chart_type": str(spec.type),
            },
        )

    def _create_figure(self, dataframe: pl.DataFrame, spec: ChartSpec) -> go.Figure:
        """Cria um objeto Plotly conforme o tipo de gráfico solicitado."""
        match spec.type:
            case ChartType.BAR:
                figure = go.Figure(
                    data=[
                        go.Bar(
                            x=dataframe[spec.x].to_list(),
                            y=dataframe[spec.y].to_list(),
                        ),
                    ],
                )

            case ChartType.LINE:
                figure = go.Figure(
                    data=[
                        go.Scatter(
                            x=dataframe[spec.x].to_list(),
                            y=dataframe[spec.y].to_list(),
                            mode="lines",
                        ),
                    ],
                )

            case ChartType.HIST:
                figure = go.Figure(
                    data=[
                        go.Histogram(
                            x=dataframe[spec.x].to_list(),
                            y=dataframe[spec.y].to_list(),
                        ),
                    ],
                )

            case chart_type:
                raise ValueError(f"Unsuppored chart type '{chart_type}'")

        if spec.title is not None:
            figure.update_layout(title=spec.title)

        return figure
