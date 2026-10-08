from pydantic import BaseModel
from uuid import UUID
from typing import Optional

from dataflow_domain import ExecutionStatus, Analysis, Execution
from .analysis import AnalysisRequest


class ExecutionRequest(BaseModel):
    analysis: AnalysisRequest

    def to_domain(self) -> Analysis:
        return self.analysis.to_domain()

class ExecutionResponse(BaseModel):
    id:             UUID
    analysis_id:    UUID
    status:         ExecutionStatus
    error:          Optional[str]

    @classmethod
    def from_domain(cls, execution: Execution) -> ExecutionResponse:
        return ExecutionResponse(
            id=execution.id,
            analysis_id=execution.analysis_id,
            status=execution.status,
            error=execution.error,
        )