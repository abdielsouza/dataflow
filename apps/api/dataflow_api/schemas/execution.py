from uuid import UUID

from dataflow_domain import Analysis, Execution, ExecutionStatus
from pydantic import BaseModel

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
    error:          str | None

    @classmethod
    def from_domain(cls, execution: Execution) -> ExecutionResponse:
        """Cria um payload de resposta a partir de um objeto de execução do domínio."""
        return ExecutionResponse(
            id=execution.id,
            analysis_id=execution.analysis_id,
            status=execution.status,
            error=execution.error,
        )