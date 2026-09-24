from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class Dataset:
    name: str
    source: str
    id: UUID = field(default_factory=uuid4)
