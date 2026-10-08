from fastapi import Depends

from .base import AbstractRouter
from ..schemas import ExecutionResponse, ExecutionRequest
from ..services import ExecutionService
from ..dependencies import get_execution_service


class ExecutionRouter(AbstractRouter):
    prefix = "/executions"
    tags = ("executions",)

    def _register_routes(self):
        self.router.add_api_route("", self.execute, methods=["POST"], response_model=ExecutionResponse)
    
    def execute(
        self,
        request: ExecutionRequest,
        service: ExecutionService = Depends(get_execution_service),
    ) -> ExecutionResponse:
        analysis = request.to_domain()
        execution = service.execute(analysis)

        return ExecutionResponse.from_domain(execution)