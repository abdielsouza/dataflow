from uuid import uuid4
from typing import cast

import pytest

from dataflow_api.schemas import (
    AnalysisRequest,
    DatasetRequest,
    OperationEdgeRequest,
    OperationRequest,
)
from dataflow_domain import Analysis
from dataflow_domain.operations import FilterOperation, SortOperation


def test_analysis_request_to_domain() -> None:
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
                    "operator": "==",
                    "value": "MG",
                },
            }),
            OperationRequest.model_validate({
                "id": sort_id,
                "type": "sort",
                "parameters": {
                    "columns": ["vendas"],
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

    filter_node = next(
        node for node in analysis.graph.nodes if isinstance(node.operation, FilterOperation)
    )
    sort_node = next(
        node for node in analysis.graph.nodes if isinstance(node.operation, SortOperation)
    )

    assert cast(FilterOperation, filter_node.operation).column == "estado"
    assert cast(FilterOperation, filter_node.operation).operator == "=="
    assert cast(FilterOperation, filter_node.operation).value == "MG"
    assert cast(SortOperation, sort_node.operation).columns == ("vendas",)
    assert cast(SortOperation, sort_node.operation).descending is True


def test_analysis_request_with_unsupported_operation_is_rejected() -> None:
    request = AnalysisRequest(
        name="Análise inválida",
        dataset=DatasetRequest.model_validate({
            "name": "Vendas",
            "source": "vendas.csv",
        }),
        operations=[
            OperationRequest.model_validate({
                "id": uuid4(),
                "type": "unknown",
                "parameters": {},
            }),
        ],
        edges=[],
    )

    with pytest.raises(ValueError, match="Unsupported operation type: unknown"):
        request.to_domain()
