from .services import ExecutionService

from dataflow_execution import ExecutionEngine


def get_execution_service():
    return ExecutionService(ExecutionEngine())