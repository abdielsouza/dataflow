from dataclasses import dataclass, field
from enum import StrEnum
from uuid import UUID, uuid4
from typing import Optional

from .artifact import Artifact


class ExecutionStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Execution:
    analysis_id: UUID
    id: UUID = field(default_factory=uuid4)
    status: ExecutionStatus = ExecutionStatus.PENDING
    artifacts: list[Artifact] = field(default_factory=list)
    error: Optional[str] = None
