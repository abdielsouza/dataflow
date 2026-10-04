"""Operações concretas do domínio aplicáveis em fluxos de análise."""

from .group_by import GroupByOperation
from .filter import FilterOperation
from .sort import SortOperation
from .chart import CreateChartOperation

__all__ = [
    "GroupByOperation",
    "FilterOperation",
    "SortOperation",
    "CreateChartOperation",
]
