import polars as pl
from typing import cast

from dataflow_domain import Analysis, ExecutionStatus, GroupByOperation
from dataflow_execution import ExecutionEngine


def test_analysis_execution() -> None:
    dataframe = pl.DataFrame({
        "estado": ["MG", "MG", "SP"],
        "faturamento": [100, 200, 500],
    })

    analysis = Analysis(
        name="Faturamento por estado",
        dataset_id=None,
    )

    analysis.add_operation(
        GroupByOperation(
            columns=("estado",),
            aggregations={
                "faturamento": "sum",
            }
        )
    )

    execution = ExecutionEngine().run(analysis, dataframe)

    assert execution.status == ExecutionStatus.COMPLETED
    assert len(execution.artifacts) == 1

    result = cast(pl.DataFrame, execution.artifacts[0].data).sort("estado")

    assert result["estado"].to_list() == ["MG", "SP"]
    assert result["faturamento"].to_list() == [300, 500]