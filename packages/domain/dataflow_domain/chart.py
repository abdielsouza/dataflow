"""Especificações de gráficos usadas na criação de artefatos visuais."""

from dataclasses import dataclass
from enum import StrEnum


class ChartType(StrEnum):
    """Tipos de visualização suportados pelo motor de gráficos."""

    BAR = "bar"
    PIE = "pie"
    HIST = "hist"
    LINE = "line"


@dataclass(frozen=True)
class ChartSpec:
    """Define a estrutura de um gráfico para renderização posterior."""

    type: ChartType
    x: str
    y: str
    title: str | None = None
