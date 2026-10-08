from pydantic import BaseModel
from uuid import UUID
from typing import Optional

from dataflow_domain import ExecutionStatus, Analysis, Execution
from .analysis import AnalysisRequest


class ExecutionRequest(BaseModel):
    """Requisição para disparar a execução de uma análise."""

    analysis: AnalysisRequest

    def to_domain(self) -> Analysis:
        """Converte a requisição em uma análise do domínio."""
        return self.analysis.to_domain()


class ExecutionResponse(BaseModel):
    """Resposta serializada para uma execução de análise."""

    id:             UUID
    analysis_id:    UUID
    status:         ExecutionStatus
    error:          Optional[str]

    @classmethod
    def from_domain(cls, execution: Execution) -> ExecutionResponse:
        """Cria um payload de resposta a partir de um objeto de execução do domínio."""
        return ExecutionResponse(
            id=execution.id,
            analysis_id=execution.analysis_id,
            status=execution.status,
            error=execution.error,
        )