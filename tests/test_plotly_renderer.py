import polars as pl
import pytest
from dataflow_analytics import PlotlyRenderer
from dataflow_domain import Artifact, ArtifactType, ChartSpec, ChartType


def test_render_bar_chart() -> None:
    dataframe = pl.DataFrame({"estado": ["MG", "SP"], "faturamento": [300, 500]})
    chart = ChartSpec(type=ChartType.BAR, x="estado", y="faturamento", title="Faturamento por estado")
    artifact = Artifact(type=ArtifactType.CHART, data={"spec": chart, "data": dataframe})

    rendered = PlotlyRenderer().render(artifact)

    assert rendered.data["layout"]["title"]["text"] == "Faturamento por estado"
    assert rendered.data["data"][0]["x"] == ["MG", "SP"]
    assert rendered.data["data"][0]["y"] == [300, 500]


def test_render_line_chart() -> None:
    dataframe = pl.DataFrame({"ano": [2021, 2022, 2023], "vendas": [100, 150, 200]})
    chart = ChartSpec(type=ChartType.LINE, x="ano", y="vendas", title="Vendas por ano")
    artifact = Artifact(type=ArtifactType.CHART, data={"spec": chart, "data": dataframe})

    rendered = PlotlyRenderer().render(artifact)

    assert rendered.type.value == "chart"
    assert rendered.renderer.value == "plotly"
    assert rendered.data["data"][0]["x"] == [2021, 2022, 2023]
    assert rendered.data["data"][0]["y"] == [100, 150, 200]


def test_renderer_rejects_non_chart_artifact() -> None:
    artifact = Artifact(type=ArtifactType.TABLE, data={})

    with pytest.raises(ValueError, match="requires a chart artifact"):
        PlotlyRenderer().render(artifact)
