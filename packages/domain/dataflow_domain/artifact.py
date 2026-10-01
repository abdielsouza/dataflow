from dataclasses import dataclass, field
from uuid import UUID, uuid4
from enum import StrEnum
from typing import Any

class ArtifactType(StrEnum):
    TABLE   = "table"
    CHART   = "chart"
    TEXT    = "text"

@dataclass
class Artifact:
    type: ArtifactType
    data: Any
    id: UUID = field(default_factory=uuid4)
