import polars as pl

from dataflow_analytics import PlotlyRenderer
from dataflow_domain import (
    Artifact,
    ArtifactType,
    ChartSpec,
    ChartType,
)


def test_render_bar_chart() -> None:
    dataframe = pl.DataFrame({
        "estado": ["MG", "SP"],
        "faturamento": [300, 500],
    })

    chart = ChartSpec(
        type=ChartType.BAR,
        x="estado",
        y="faturamento",
        title="Faturamento por estado",
    )

    artifact = Artifact(
        type=ArtifactType.CHART,
        data={
            "spec": chart,
            "data": dataframe,
        },
    )

    rendered = PlotlyRenderer().render(artifact)

    assert rendered["layout"]["title"]["text"] == "Faturamento por estado"
    assert rendered["data"][0]["x"] == ["MG", "SP"]
    assert rendered["data"][0]["y"] == [300, 500]