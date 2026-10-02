import polars as pl
from dataflow_domain import Artifact, ArtifactType, Operation, GroupByOperation, FilterOperation, SortOperation


class PolarsEngine:
    def execute(self, artifact: Artifact, operation: Operation) -> Artifact:
        if artifact.type != ArtifactType.TABLE:
            raise ValueError(f"Artifact must be a table")

        dataframe = artifact.data

        if isinstance(operation, GroupByOperation):
            return self._execute_group_by(dataframe, operation)
        elif isinstance(operation, FilterOperation):
            return self._execute_filter(dataframe, operation)
        elif isinstance(operation, SortOperation):
            return self._execute_sort(dataframe, operation)
        else:
            raise ValueError(f"Unsupported operation: {operation.type}")

    def _execute_group_by(self, dataframe: pl.DataFrame, operation: GroupByOperation) -> Artifact:
        aggregations = []

        for col, func in operation.aggregations.items():
            expression = getattr(pl.col(col), func)()
            aggregations.append(expression.alias(col))

        result = dataframe.group_by(list(operation.columns)).agg(aggregations)

        return Artifact(type=ArtifactType.TABLE, data=result)
    
    def _execute_filter(self, dataframe: pl.DataFrame, operation: FilterOperation) -> Artifact:
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
        result = dataframe.sort(list(operation.columns), descending=operation.descending)

        return Artifact(type=ArtifactType.TABLE, data=result)