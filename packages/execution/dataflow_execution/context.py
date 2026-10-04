"""Contexto de execução para armazenar artefatos por nó do grafo."""

from uuid import UUID

from dataflow_domain import Artifact


class ExecutionContext:
    """Mantém os artefatos intermediários produzidos durante a execução."""

    def __init__(self) -> None:
        self._artifacts: dict[UUID, Artifact] = {}

    def set_artifact(self, node_id: UUID, artifact: Artifact) -> None:
        """Salva o artefato gerado por um identificador de nó."""
        self._artifacts[node_id] = artifact

    def get_artifact(self, node_id: UUID) -> Artifact:
        """Recupera um artefato previamente armazenado para um nó."""
        try:
            return self._artifacts[node_id]
        except KeyError as error:
            raise ValueError(f"No artifact found for node '{node_id}'") from error
