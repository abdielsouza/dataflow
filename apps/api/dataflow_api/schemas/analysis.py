from pydantic import BaseModel
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
    type:   str
    x:      str
    y:      str
    title:  Optional[str] = None

    def to_domain(self) -> ChartSpec:
        return ChartSpec(
            type=ChartType(self.type),
            x=self.x,
            y=self.y,
            title=self.title,
        )


class OperationRequest(BaseModel):
    id:         UUID
    type:       str
    parameters: dict[str, Any]

    def to_domain(self) -> Operation:
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
    source: UUID
    target: UUID


class DatasetRequest(BaseModel):
    name:   str
    source: str

    def to_domain(self) -> Dataset:
        return Dataset(name=self.name, source=self.source)


class AnalysisRequest(BaseModel):
    name:       str
    dataset:    DatasetRequest
    operations: list[OperationRequest]
    edges:      list[OperationEdgeRequest]

    def to_domain(self) -> Analysis:
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