from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class Artifact:
    type: str
    data: object
    id: UUID = field(default_factory=uuid4)
