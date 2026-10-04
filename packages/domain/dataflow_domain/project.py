"""Entidade de projeto que reúne análises e recursos do domínio."""

from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class Project:
    """Representa um projeto com um identificador e um nome."""

    name: str
    id: UUID = field(default_factory=uuid4)
