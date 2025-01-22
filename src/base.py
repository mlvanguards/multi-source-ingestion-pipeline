from abc import ABC, abstractmethod
from typing import List, Any, Optional


class PipelineStep(ABC):

    @abstractmethod
    def __call__(self, *args, **kwargs):
        pass


class Pipeline:
    def __init__(self):
        self.steps: List[PipelineStep] = []

    def run(self):
        result = None
        for step in self.steps:
            result = step(result)
        return result

    def add_step(self, step: PipelineStep):
        self.steps.append(step)
        return self


class PipelineBuilder(ABC):

    @abstractmethod
    def build(self) -> Pipeline:
        pass


class BaseReader(ABC):
    @abstractmethod
    def load_items(self, *args: Any, **kwargs: Any) -> Optional[List[Any]]:
        """Load items from the input data source."""
