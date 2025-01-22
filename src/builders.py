from src.base import PipelineBuilder, Pipeline
from src.readers import JiraReader
from src.steps import LoadItemsStep


class AtlassianJiraIngestionPipeline(PipelineBuilder):

    def build(self) -> Pipeline:
        pipeline = Pipeline()

        reader = JiraReader()

        (pipeline
         .add_step(LoadItemsStep(reader))
         )
        return pipeline
