from unittest.mock import Mock

from dataflow_api import ExecutionService
from dataflow_domain import Analysis, Execution
from dataflow_execution import ExecutionEngine


def test_execute_delegates_to_engine() -> None:
    analysis = Mock(spec=Analysis)
    execution = Mock(spec=Execution)

    engine = Mock(spec=ExecutionEngine)
    engine.run.return_value = execution

    service = ExecutionService(engine)
    result = service.execute(analysis)

    engine.run.assert_called_once_with(analysis)
    assert result is execution