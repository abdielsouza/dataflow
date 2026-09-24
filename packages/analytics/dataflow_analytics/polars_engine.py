import polars as pl
from dataflow_domain import Artifact, Operation, GroupByOperation


class PolarsEngine:
    def execute(self, dataframe: pl.DataFrame, operation: Operation) -> Artifact:
        if (isinstance(operation, GroupByOperation)):
            return self._execute_group_by(dataframe, operation)
        else:
            raise ValueError

    def _execute_group_by(self, dataframe: pl.DataFrame, operation: GroupByOperation) -> Artifact:
        aggregations = []
        
        for col, func in operation.aggregations.items():
            expression = getattr(pl.col(col), func)()
            aggregations.append(expression.alias(col))

        result = dataframe.group_by(list(operation.columns)).agg(aggregations)

        return Artifact(type="table", data=result)
