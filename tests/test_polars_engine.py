import polars as pl

from dataflow_analytics import PolarsEngine
from dataflow_domain import Artifact, ArtifactType, FilterOperation, GroupByOperation, SortOperation


def test_group_by_sum() -> None:
    dataframe = pl.DataFrame({"estado": ["MG", "MG", "SP"], "faturamento": [100, 200, 500]})
    artifact = Artifact(type=ArtifactType.TABLE, data=dataframe)
    operation = GroupByOperation(columns=("estado",), aggregations={"faturamento": "sum"})

    result = PolarsEngine().execute((artifact,), operation)

    assert result.type == ArtifactType.TABLE
    result_dataframe = result.data.sort("estado")
    assert result_dataframe["estado"].to_list() == ["MG", "SP"]
    assert result_dataframe["faturamento"].to_list() == [300, 500]


def test_filter_and_sort_operations() -> None:
    dataframe = pl.DataFrame({"estado": ["MG", "SP", "MG"], "vendas": [100, 300, 200]})
    artifact = Artifact(type=ArtifactType.TABLE, data=dataframe)
    engine = PolarsEngine()

    filtered = engine.execute((artifact,), FilterOperation(column="estado", operator="==", value="MG"))
    sorted_result = engine.execute((filtered,), SortOperation(columns=("vendas",), descending=True))

    assert filtered.data["estado"].to_list() == ["MG", "MG"]
    assert sorted_result.data["vendas"].to_list() == [200, 100]