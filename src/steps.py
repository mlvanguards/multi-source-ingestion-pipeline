from typing import List, Dict, Any, Type

from src.base import PipelineStep, BaseReader


class LoadItemsStep(PipelineStep):
    def __init__(self, reader: BaseReader):
        self.reader = reader

    def __call__(self, *args, **kwargs) -> List[Dict[str, Any]]:
        return self.reader.load_items()
