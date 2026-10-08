from uuid import uuid4
from typing import cast

from dataflow_domain import Analysis
from dataflow_domain.operations import (
    FilterOperation,
    SortOperation,
)
from dataflow_api.schemas import (
    AnalysisRequest,
    DatasetRequest,
    OperationRequest,
    OperationEdgeRequest,
)


def test_analysis_request_to_domain():
    filter_id = uuid4()
    sort_id = uuid4()

    request = AnalysisRequest(
        name="Análise de Vendas",
        dataset=DatasetRequest.model_validate({
            "name": "Vendas",
            "source": "vendas.csv",
        }),
        operations=[
            OperationRequest.model_validate({
                "id": filter_id,
                "type": "filter",
                "parameters": {
                    "column": "estado",
                    "operator": "eq",
                    "value": "MG",
                },
            }),
            OperationRequest.model_validate({
                "id": sort_id,
                "type": "sort",
                "parameters": {
                    "columns": ["faturamento"],
                    "descending": True,
                },
            }),
        ],
        edges=[
            OperationEdgeRequest.model_validate({
                "source": filter_id,
                "target": sort_id,
            }),
        ],
    )

    analysis = request.to_domain()

    assert isinstance(analysis, Analysis)
    assert analysis.name == "Análise de Vendas"

    assert analysis.dataset.name == "Vendas"
    assert analysis.dataset.source == "vendas.csv"

    assert len(analysis.graph.nodes) == 2
    assert len(analysis.graph.edges) == 1

    nodes = analysis.graph.nodes

    filter_node = next(node for node in nodes if isinstance(node.operation, FilterOperation))
    sort_node = next(node for node in nodes if isinstance(node.operation, SortOperation))

    assert cast(FilterOperation, filter_node.operation).column == "estado"
    assert cast(FilterOperation, filter_node.operation).operator == "eq"
    assert cast(FilterOperation, filter_node.operation).value == "MG"
    
    assert cast(SortOperation, sort_node.operation).columns == ("faturamento",)
    assert cast(SortOperation, sort_node.operation).descending is True