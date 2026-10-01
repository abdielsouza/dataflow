from dataclasses import dataclass
from typing import Optional
from enum import StrEnum

class ChartType(StrEnum):
    BAR     = "bar"
    PIE     = "pie"
    HIST    = "hist"
    LINE    = "line"

@dataclass(frozen=True)
class ChartSpec:
    type:       ChartType
    x:          str
    y:          str
    title:      Optional[str] = None