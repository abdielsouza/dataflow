"""Estado e rastreio da execução de uma análise."""

from dataclasses import dataclass, field
from enum import StrEnum
from uuid import UUID, uuid4
from typing import Optional

from .artifact import Artifact


class ExecutionStatus(StrEnum):
    """Possíveis estados de uma execução analítica."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Execution:
    """Armazena o resultado da execução de uma análise com seus artefatos."""

    analysis_id: UUID
    id: UUID = field(default_factory=uuid4)
    status: ExecutionStatus = ExecutionStatus.PENDING
    artifacts_by_node: dict[UUID, Artifact] = field(default_factory=dict)
    error: Optional[str] = None

    @property
    def artifacts(self) -> tuple[Artifact, ...]:
        """Retorna os artefatos produzidos em ordem de armazenamento."""
        return tuple(self.artifacts_by_node.values())
