import polars as pl

from dataflow_domain import (
    Artifact,
    ArtifactType,
    GroupByOperation,
)
from dataflow_analytics import PolarsEngine


def test_group_by_sum() -> None:
    dataframe = pl.DataFrame({
        "estado": ["MG", "MG", "SP"],
        "faturamento": [100, 200, 500],
    })

    artifact = Artifact(
        type=ArtifactType.TABLE,
        data=dataframe,
    )

    operation = GroupByOperation(
        columns=("estado",),
        aggregations={
            "faturamento": "sum",
        },
    )

    result = PolarsEngine().execute((artifact,), operation)

    assert result.type == ArtifactType.TABLE

    result_dataframe = result.data.sort("estado")

    assert result_dataframe["estado"].to_list() == ["MG", "SP"]
    assert result_dataframe["faturamento"].to_list() == [300, 500]