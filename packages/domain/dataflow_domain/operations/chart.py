"""Operação para transformar um artefato tabular em gráfico."""

from dataclasses import dataclass

from ..chart import ChartSpec
from ..operation import Operation


@dataclass(frozen=True)
class CreateChartOperation(Operation):
    """Cria um artefato de gráfico a partir de uma especifiação visual."""

    chart: ChartSpec

    @property
    def type(self) -> str:
        """Retorna o identificador estático da operação."""
        return "create_chart"
