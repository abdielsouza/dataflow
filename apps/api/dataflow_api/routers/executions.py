"""Endpoints de execução de análises via API HTTP."""

from fastapi import Depends

from .base import AbstractRouter
from ..schemas import ExecutionResponse, ExecutionRequest
from ..services import ExecutionService
from ..dependencies import get_execution_service, get_current_user
from .datasets import _owned_source

from dataflow_domain import User


class ExecutionRouter(AbstractRouter):
    """Expõe operações para iniciar e monitorar execuções de análise."""

    prefix = "/executions"
    tags = ("executions",)

    def _register_routes(self):
        """Registra a rota de criação de execução da análise."""
        self.router.add_api_route("", self.execute, methods=["POST"], response_model=ExecutionResponse)

    def execute(
        self,
        request: ExecutionRequest,
        service: ExecutionService = Depends(get_execution_service),
        user: User = Depends(get_current_user),
    ) -> ExecutionResponse:
        """Validate dataset ownership, then execute the requested analysis."""
        _owned_source(request.analysis.dataset.source, str(user.id))
        analysis = request.to_domain()
        execution = service.execute(analysis)

        return ExecutionResponse.from_domain(execution)