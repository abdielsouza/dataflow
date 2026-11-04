"""Implementação de execução de operações analíticas usando Polars."""

import polars as pl
from dataflow_domain import (
    Artifact,
    ArtifactType,
    ConcatOperation,
    FilterOperation,
    GroupByOperation,
    Operation,
    SortOperation,
)


class PolarsEngine:
    """Executa operações do domínio sobre tabelas Polars."""

    def execute(self, artifacts: tuple[Artifact, ...], operation: Operation) -> Artifact:
        """Aplica uma operação de análise a um artefato tabular."""
        if any(artifact.type != ArtifactType.TABLE for artifact in artifacts):
            raise ValueError("Artifacts must be tables")

        if isinstance(operation, GroupByOperation):
            self._require_single_input(artifacts)
            return self._execute_group_by(artifacts[0].data, operation)
        
        elif isinstance(operation, FilterOperation):
            self._require_single_input(artifacts)
            return self._execute_filter(artifacts[0].data, operation)
        
        elif isinstance(operation, SortOperation):
            self._require_single_input(artifacts)
            return self._execute_sort(artifacts[0].data, operation)
        
        elif isinstance(operation, ConcatOperation):
            return self._execute_concat(artifacts)
        
        else:
            raise TypeError(f"Unsupported operation: {operation.type}")

    def _execute_group_by(self, dataframe: pl.DataFrame, operation: GroupByOperation) -> Artifact:
        """Agrupa e agrega uma tabela conforme a operação informada."""
        aggregations = []

        for col, func in operation.aggregations.items():
            expression = getattr(pl.col(col), func)()
            aggregations.append(expression.alias(col))

        result = dataframe.group_by(list(operation.columns)).agg(aggregations)

        return Artifact(type=ArtifactType.TABLE, data=result)

    def _execute_filter(self, dataframe: pl.DataFrame, operation: FilterOperation) -> Artifact:
        """Filtra uma tabela por coluna, operador e valor."""
        column = pl.col(operation.column)

        match operation.operator:
            case "==":
                expression = column == operation.value

            case "!=":
                expression = column != operation.value

            case ">=":
                expression = column >= operation.value

            case "<=":
                expression = column <= operation.value

            case ">":
                expression = column > operation.value

            case "<":
                expression = column < operation.value

            case op:
                raise ValueError(f"Unsupported filter operator: {op}")

        result = dataframe.filter(expression)

        return Artifact(type=ArtifactType.TABLE, data=result)

    def _execute_sort(self, dataframe: pl.DataFrame, operation: SortOperation) -> Artifact:
        """Ordena uma tabela segundo as colunas e a direção configuradas."""
        result = dataframe.sort(list(operation.columns), descending=operation.descending)

        return Artifact(type=ArtifactType.TABLE, data=result)

    def _execute_concat(self, artifacts: tuple[Artifact, ...]) -> Artifact:
        """Concatena vários artefatos tabulares em um único DataFrame."""
        if not artifacts:
            raise ValueError("Concat requires at least one input.")

        dataframes = tuple(artifact.data for artifact in artifacts)

        return Artifact(type=ArtifactType.TABLE, data=pl.concat(dataframes))

    def _require_single_input(self, artifacts: tuple[Artifact, ...]) -> None:
        """Valida que a operação receba exatamente um artefato de entrada."""
        if len(artifacts) != 1:
            raise ValueError("This operation requires exactly one input.")