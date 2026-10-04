from pathlib import Path

from dataflow_domain import (
    Analysis,
    # Artifact,
    # ArtifactType,
    # ChartSpec,
    # ChartType,
    # CreateChartOperation,
    Dataset,
    ExecutionStatus,
    # FilterOperation,
    # GroupByOperation,
)
from dataflow_execution import ExecutionEngine
# from dataflow_storage import DatasetLoader

def test_complete_analysis_pipeline(tmp_path: Path = Path(".")) -> None:
    dataset_path = tmp_path / "vendas.csv"
    dataset_path.write_text("estado,vendas\nMG,100\nMG,200\nSP,500\nRJ,50\n")

    dataset = Dataset(name="Vendas", source=str(dataset_path.resolve()))
    analysis = Analysis(name="Análise de Vendas", dataset=dataset)

    execution = ExecutionEngine().run(analysis)

    assert execution.status == ExecutionStatus.COMPLETED
    assert execution.error is None