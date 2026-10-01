from dataclasses import dataclass

from ..chart import ChartSpec
from ..operation import Operation


@dataclass(frozen=True)
class CreateChartOperation(Operation):
    chart: ChartSpec

    @property
    def type(self) -> str:
        return "create_chart"