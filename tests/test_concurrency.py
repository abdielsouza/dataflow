import polars as pl

from dataflow_domain import Artifact, ArtifactType, FilterOperation, GroupByOperation, OperationNode
from dataflow_execution import ConcurrentStageExecutor


def test_concurrent_stage_executor() -> None:
    filter_operation = FilterOperation(column="faturamento", operator=">", value=100)
    groupby_operation = GroupByOperation(columns=("estado",), aggregations={"faturamento": "sum"})
    executor = ConcurrentStageExecutor()
    nodes = (
        OperationNode(operation=filter_operation),
        OperationNode(operation=groupby_operation),
    )

    def execute_node(node: OperationNode) -> Artifact:
        return Artifact(type=ArtifactType.TABLE, data=node.id)

    results = executor.execute(nodes, execute_node)

    assert set(results) == set(nodes)
    assert results[nodes[0]].data == nodes[0].id
    assert results[nodes[1]].data == nodes[1].id

    dataframe = pl.DataFrame({"estado": ["MG", "MG", "SP"], "faturamento": [100, 200, 500]})
    assert dataframe["estado"].len() == 3