from dataflow_domain import (
    Artifact,
    ArtifactType,
    ChartSpec,
    ChartType,
    CreateChartOperation,
)


def test_chart_spec() -> None:
    chart = ChartSpec(
        type=ChartType.BAR,
        x="estado",
        y="faturamento",
        title="Faturamento por estado",
    )

    assert chart.type == ChartType.BAR
    assert chart.x == "estado"
    assert chart.y == "faturamento"


def test_create_chart_operation() -> None:
    chart = ChartSpec(
        type=ChartType.BAR,
        x="estado",
        y="faturamento",
        title="Faturamento por estado",
    )

    operation = CreateChartOperation(chart=chart)

    assert operation.type == "create_chart"


def test_chart_artifact() -> None:
    chart = ChartSpec(
        type=ChartType.BAR,
        x="estado",
        y="faturamento",
        title="Faturamento por estado",
    )

    artifact = Artifact(
        type=ArtifactType.CHART,
        data=chart,
    )

    assert artifact.type == ArtifactType.CHART
    assert artifact.data == chart
