from pathlib import Path

from dataflow_domain import (
    Analysis,
    ArtifactType,
    ChartSpec,
    ChartType,
    CreateChartOperation,
    Dataset,
    ExecutionStatus,
    FilterOperation,
    GroupByOperation,
)
from dataflow_execution import ExecutionEngine


def test_complete_analysis_pipeline(tmp_path: Path = Path(".")) -> None:
    dataset_path = tmp_path / "vendas.csv"

    dataset_path.write_text("estado,vendas\nMG,100\nMG,200\nSP,500\nRJ,50\n")

    dataset = Dataset(name="Vendas", source=str(dataset_path.resolve()))
    analysis = Analysis(name="Análise de Vendas", dataset=dataset)

    analysis.add_operation(
        FilterOperation(
            column="vendas",
            operator=">",
            value=50,
        )
    )

    analysis.add_operation(
        GroupByOperation(
            columns=("estado",),
            aggregations={
                "vendas": "sum",
            },
        )
    )

    analysis.add_operation(
        CreateChartOperation(
            chart=ChartSpec(
                type=ChartType.BAR,
                x="estado",
                y="vendas",
                title="Vendas por estado",
            ),
        )
    )

    execution = ExecutionEngine().run(analysis)

    print(execution.error)

    assert execution.status == ExecutionStatus.COMPLETED
    assert execution.error is None

    assert len(execution.artifacts) == 3

    filter_result = execution.artifacts[0]
    group_result = execution.artifacts[1]
    chart_result = execution.artifacts[2]

    assert filter_result.type == ArtifactType.TABLE
    assert group_result.type == ArtifactType.TABLE
    assert chart_result.type == ArtifactType.CHART
