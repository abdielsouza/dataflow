from pathlib import Path

from dataflow_domain import Analysis, Dataset, ExecutionStatus, FilterOperation, SortOperation
from dataflow_execution import ExecutionEngine


def test_complete_analysis_pipeline(tmp_path: Path) -> None:
    dataset_path = tmp_path / "vendas.csv"
    dataset_path.write_text("estado,vendas\nMG,100\nMG,200\nSP,500\nRJ,50\n")

    analysis = Analysis(name="Análise de Vendas", dataset=Dataset(name="Vendas", source=str(dataset_path)))
    source = analysis.add_operation(FilterOperation(column="estado", operator="==", value="MG"))
    target = analysis.add_operation(SortOperation(columns=("vendas",), descending=True))
    analysis.graph.add_edge(source, target)

    execution = ExecutionEngine().run(analysis)

    assert execution.status == ExecutionStatus.COMPLETED
    assert execution.error is None
    assert execution.artifacts_by_node[target.id].data["estado"].to_list() == ["MG", "MG"]
    assert execution.artifacts_by_node[target.id].data["vendas"].to_list() == [200, 100]