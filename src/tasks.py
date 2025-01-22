import ray

from typing import List

from src.manager import ingestion_manager


@ray.remote
def ingest_source(connectors: List[str]) -> None:
    for connector in connectors:
        pipelines = ingestion_manager.create_pipeline(
            connector
        )
        for p in pipelines:
            p.run()




