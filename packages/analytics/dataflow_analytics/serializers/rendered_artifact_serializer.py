from typing import Any

from ..models import RenderedArtifact


class RenderedArtifactSerializer:
    def serialize(self, artifact: RenderedArtifact) -> dict[str, Any]:
        return {
            "type": artifact.type,
            "renderer": artifact.renderer,
            "data": artifact.data,
            "metadata": artifact.metadata,
        }