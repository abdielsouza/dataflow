"""Dependências compartilhadas da API de execução."""

from .services import ExecutionService

from dataflow_execution import ExecutionEngine


def get_execution_service() -> ExecutionService:
    """Cria a instância de serviço de execução usada pelos endpoints."""
    return ExecutionService(ExecutionEngine())