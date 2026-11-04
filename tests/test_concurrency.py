import polars as pl
from dataflow_domain import Artifact, ArtifactType
from dataflow_execution import ConcurrentStageExecutor
from hyperway import Unit


def test_concurrent_stage_executor() -> None:
    executor = ConcurrentStageExecutor()
    nodes = (
        Unit(lambda value: value, name="first"),
        Unit(lambda value: value, name="second"),
    )

    def execute_node(node: Unit) -> Artifact:
        return Artifact(type=ArtifactType.TABLE, data=node.name)

    results = executor.execute(nodes, execute_node)

    assert set(results) == set(nodes)
    assert results[nodes[0]].data == "first"
    assert results[nodes[1]].data == "second"

    dataframe = pl.DataFrame({"estado": ["MG", "MG", "SP"], "faturamento": [100, 200, 500]})
    assert dataframe["estado"].len() == 3