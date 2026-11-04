"""Operações concretas do domínio aplicáveis em fluxos de análise."""

from .chart import CreateChartOperation
from .concat import ConcatOperation
from .filter import FilterOperation
from .group_by import GroupByOperation
from .sort import SortOperation

__all__ = [
    "ConcatOperation",
    "CreateChartOperation",
    "FilterOperation",
    "GroupByOperation",
    "SortOperation",
]
