from dataflow_analytics import (
    RenderedArtifact,
    RenderedArtifactSerializer,
    RenderedArtifactType,
    RendererType,
)


def test_serialize_rendered_artifact() -> None:
    artifact_data = {
        "data": [{"type": "bar", "x": ["MG", "SP"], "y": [300, 500]}],
        "layout": {"title": {"text": "Faturamento por estado"}},
    }
    artifact_metadata = {"chart_type": "bar"}

    artifact = RenderedArtifact(
        type=RenderedArtifactType.CHART,
        renderer=RendererType.PLOTLY,
        data=artifact_data,
        metadata=artifact_metadata,
    )

    serialized = RenderedArtifactSerializer().serialize(artifact)

    assert serialized == {
        "type": RenderedArtifactType.CHART,
        "renderer": RendererType.PLOTLY,
        "data": artifact_data,
        "metadata": artifact_metadata,
    }
