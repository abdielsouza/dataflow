from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class Project:
    name: str
    id: UUID = field(default_factory=uuid4)
