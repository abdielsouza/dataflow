import polars as pl
from typing import cast

from dataflow_analytics import PolarsEngine
from dataflow_domain import GroupByOperation

def test_group_by_sum() -> None:
    dataframe = pl.DataFrame({
        "estado": ["MG", "MG", "SP"],
        "faturamento": [100, 200, 500],
    })

    operation = GroupByOperation(
        columns=("estado",),
        aggregations={
            "faturamento": "sum",
        }
    )

    artifact = PolarsEngine().execute(dataframe, operation)

    result = cast(pl.DataFrame, artifact.data).sort("estado")

    assert result["estado"].to_list() == ["MG", "SP"]
    assert result["faturamento"].to_list() == [300, 500]