"""Representação de fontes de dados no domínio."""

from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class Dataset:
    """Descreve um conjunto de dados a partir de uma origem informada."""

    name: str
    source: str
    id: UUID = field(default_factory=uuid4)
