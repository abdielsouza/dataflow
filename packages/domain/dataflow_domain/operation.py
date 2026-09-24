from abc import ABC, abstractmethod


class Operation(ABC):
    """
    A data transformation that can be executed by
    an analytics engine.
    """

    @property
    @abstractmethod
    def type(self) -> str:
        ...
