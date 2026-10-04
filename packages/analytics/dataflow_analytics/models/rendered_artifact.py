"""Modelos que representam artefatos gráficos após o processo de renderização."""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class RenderedArtifactType(StrEnum):
    """Tipos de artefato que podem ser gerados como resultado do render."""

    CHART = "chart"
    OTHER = "other"


class RendererType(StrEnum):
    """Renderizadores suportados para a conversão de artefatos em visualizações."""

    PLOTLY = "plotly"
    MATPLOTLIB = "matplotlib"
    VEGA = "vega"


type RendererArtifactData = dict[str, Any]
type RendererArtifactMetadata = dict[str, Any]


@dataclass(frozen=True)
class RenderedArtifact:
    """Estrutura final de um artefato gráfico serializável para exibição."""

    type: RenderedArtifactType
    renderer: RendererType
    data: RendererArtifactData
    metadata: RendererArtifactMetadata = field(default_factory=dict)
