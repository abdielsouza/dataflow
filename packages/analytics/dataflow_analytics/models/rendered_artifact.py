from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class RenderedArtifactType(StrEnum):
    CHART = "chart"
    OTHER = "other"

class RendererType(StrEnum):
    PLOTLY      = "plotly"
    MATPLOTLIB  = "matplotlib"
    VEGA        = "vega"

type RendererArtifactData = dict[str, Any]
type RendererArtifactMetadata = dict[str, Any]

@dataclass(frozen=True)
class RenderedArtifact:
    type:       RenderedArtifactType
    renderer:   RendererType
    data:       RendererArtifactData
    metadata:   RendererArtifactMetadata = field(default_factory=dict)