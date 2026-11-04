from pathlib import Path

from dataflow_domain import (
    Analysis,
    ConcatOperation,
    Dataset,
    ExecutionStatus,
    FilterOperation,
    SortOperation,
)
from dataflow_execution import ExecutionEngine, ExecutionStrategy


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


def test_execution_engine_dispatches_each_stage_to_strategy(tmp_path: Path) -> None:
    dataset_path = tmp_path / "vendas.csv"
    dataset_path.write_text("estado,vendas\nMG,100\nSP,500\n")
    analysis = Analysis(name="Análise", dataset=Dataset(name="Vendas", source=str(dataset_path)))
    analysis.add_operation(FilterOperation(column="estado", operator="==", value="MG"))
    analysis.add_operation(SortOperation(columns=("vendas",), descending=True))

    class RecordingStrategy(ExecutionStrategy):
        def __init__(self) -> None:
            self.stage_sizes: list[int] = []

        def execute(self, nodes, execute_node):
            self.stage_sizes.append(len(nodes))
            return {node: execute_node(node) for node in nodes}

    strategy = RecordingStrategy()
    execution = ExecutionEngine(strategy=strategy).run(analysis)

    assert execution.status == ExecutionStatus.COMPLETED
    assert strategy.stage_sizes == [2]


def test_execution_engine_preserves_fan_in_for_concat(tmp_path: Path) -> None:
    dataset_path = tmp_path / "vendas.csv"
    dataset_path.write_text("estado,vendas\nMG,100\nSP,200\nRJ,300\n")
    analysis = Analysis(name="Análise", dataset=Dataset(name="Vendas", source=str(dataset_path)))
    minas = analysis.add_operation(FilterOperation(column="estado", operator="==", value="MG"))
    sao_paulo = analysis.add_operation(FilterOperation(column="estado", operator="==", value="SP"))
    concat = analysis.add_operation(ConcatOperation())
    analysis.graph.add_edge(minas, concat)
    analysis.graph.add_edge(sao_paulo, concat)

    execution = ExecutionEngine().run(analysis)

    assert execution.status == ExecutionStatus.COMPLETED
    assert execution.artifacts_by_node[concat.id].data["estado"].to_list() == ["MG", "SP"]