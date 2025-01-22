from typing import Dict, List, Type

from src.base import PipelineBuilder, Pipeline
from src.builders import AtlassianJiraIngestionPipeline


class PipelineManager:

    def __init__(self):
        self.builders: Dict[str, List[Type[PipelineBuilder]]] = {}

    def register(self, source_type: str, factories: List[Type[PipelineBuilder]]) -> None:
        self.builders[source_type] = factories

    def create_pipeline(
            self,
            source_type: str,
    ) -> List[Pipeline]:
        instances = []
        if source_type not in self.builders:
            raise ValueError(f'Unsupported source type {source_type} not registered')

        builders = self.builders.get(source_type)
        for builder in builders:
            instances.append(builder().build())

        return instances


ingestion_manager = PipelineManager()

ingestion_manager.register("atlassian", [AtlassianJiraIngestionPipeline])

