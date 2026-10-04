"""Serialização de artefatos renderizados em dicionários JSON-compatíveis."""

from typing import Any

from ..models import RenderedArtifact


class RenderedArtifactSerializer:
    """Converte um objeto de artefato renderizado em estrutura serializável."""

    def serialize(self, artifact: RenderedArtifact) -> dict[str, Any]:
        """Retorna um dicionário com os campos públicos do artefato."""
        return {
            "type": artifact.type,
            "renderer": artifact.renderer,
            "data": artifact.data,
            "metadata": artifact.metadata,
        }
