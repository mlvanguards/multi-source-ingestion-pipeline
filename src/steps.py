from typing import List, Dict, Any

from src.base import PipelineStep, BaseReader


class LoadItemsStep(PipelineStep):
    def __init__(self, reader: BaseReader, task_id: str):
        self.reader = reader
        self.task_id = task_id

    def __call__(self, *args, **kwargs) -> List[Dict[str, Any]]:
        return self.reader.load_items()
