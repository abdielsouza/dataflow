"""Serviço de aplicação para orquestrar execuções de análise."""

from dataflow_domain import Execution, Analysis
from dataflow_execution import ExecutionEngine


class ExecutionService:
    """Encapsula a engine de execução e fornece uma API simples para o endpoint."""

    def __init__(self, engine: ExecutionEngine) -> None:
        """Cria o serviço com uma engine de execução específica."""
        self._engine = engine

    def execute(self, analysis: Analysis) -> Execution:
        """Executa uma análise e retorna o registro do resultado da operação."""
        return self._engine.run(analysis)