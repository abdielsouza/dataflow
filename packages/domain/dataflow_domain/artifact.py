"""Artefatos produzidos e consumidos durante a execução da análise."""

from dataclasses import dataclass, field
from uuid import UUID, uuid4
from enum import StrEnum
from typing import Any


class ArtifactType(StrEnum):
    """Tipos de artefato reconhecidos pelo sistema."""

    TABLE = "table"
    CHART = "chart"
    TEXT = "text"


@dataclass
class Artifact:
    """Representa um resultado intermediário ou final de uma operação."""

    type: ArtifactType
    data: Any
    id: UUID = field(default_factory=uuid4)
