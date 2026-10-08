from dataflow_domain import Execution, Analysis
from dataflow_execution import ExecutionEngine


class ExecutionService:
    def __init__(self, engine: ExecutionEngine) -> None:
        self._engine = engine

    def execute(self, analysis: Analysis) -> Execution:
        return self._engine.run(analysis)