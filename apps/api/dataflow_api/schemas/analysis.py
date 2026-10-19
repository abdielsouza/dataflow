from pydantic import BaseModel, ConfigDict
from uuid import UUID
from typing import Optional, Any

from dataflow_domain import Operation, Dataset, Analysis
from dataflow_domain.chart import ChartSpec, ChartType
from dataflow_domain.operations import (
    ConcatOperation,
    CreateChartOperation,
    FilterOperation,
    GroupByOperation,
    SortOperation,
)


class ChartRequest(BaseModel):
    """Representa a especificação de um gráfico enviada pela API."""

    type:   str
    x:      str
    y:      str
    title:  Optional[str] = None

    def to_domain(self) -> ChartSpec:
        """Converte a requisição em uma especificação de gráfico do domínio."""
        return ChartSpec(
            type=ChartType(self.type),
            x=self.x,
            y=self.y,
            title=self.title,
        )


class OperationRequest(BaseModel):
    """Representa uma operação analítica recebida pela API."""

    id:         UUID
    type:       str
    parameters: dict[str, Any]

    def to_domain(self) -> Operation:
        """Cria a operação correspondente no modelo de domínio analítico."""
        match self.type:
            case "filter":
                return FilterOperation(
                    column=self.parameters["column"],
                    operator=self.parameters["operator"],
                    value=self.parameters["value"],
                )

            case "group_by":
                return GroupByOperation(
                    columns=tuple(self.parameters["columns"]),
                    aggregations=self.parameters["aggregations"],
                )

            case "sort":
                return SortOperation(
                    columns=tuple(self.parameters["columns"]),
                    descending=self.parameters.get(
                        "descending",
                        False,
                    ),
                )

            case "concat":
                return ConcatOperation()

            case "create_chart":
                chart = ChartRequest(
                    **self.parameters["chart"]
                )

                return CreateChartOperation(
                    chart=chart.to_domain()
                )

            case _:
                raise ValueError(
                    f"Unsupported operation type: {self.type}"
                )


class OperationEdgeRequest(BaseModel):
    """Descreve uma aresta entre duas operações em um grafo de análise."""

    source: UUID
    target: UUID


class DatasetRequest(BaseModel):
    """Define a origem de dados de uma análise recebida pela API."""

    name:   str
    source: str

    def to_domain(self) -> Dataset:
        """Converte a fonte de dados em um modelo de domínio."""
        return Dataset(name=self.name, source=self.source)


class AnalysisRequest(BaseModel):
    """Estrutura completa de uma análise enviada pela API."""

    name:       str
    dataset:    DatasetRequest
    operations: list[OperationRequest]
    edges:      list[OperationEdgeRequest]

    def to_domain(self) -> Analysis:
        """Transforma a requisição em um objeto de domínio com grafo e operações."""
        analysis = Analysis(name=self.name, dataset=self.dataset.to_domain())
        nodes = {}

        for operation_request in self.operations:
            operation = operation_request.to_domain()
            node = analysis.add_operation(operation)

            if operation_request.id is not None:
                nodes[operation_request.id] = node
            else:
                nodes[node.id] = node

        for edge in self.edges:
            analysis.graph.add_edge(nodes[edge.source], nodes[edge.target])

        return analysis


class SavedDatasetResponse(BaseModel):
    name:   str
    source: str


class SavedAnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:         UUID
    dataset_id: UUID
    name:       str
    dataset:    SavedDatasetResponse
    definition: dict[str, Any]
    created_at: str
    updated_at: str


class AnalysisListItem(BaseModel):
    id:         UUID
    dataset_id: UUID
    name:       str
    dataset:    SavedDatasetResponse
    created_at: str
    updated_at: str