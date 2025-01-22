from src.tasks import ingest_source

connectors = ['atlassian']

results = ingest_source.remote(connectors)
print(results)
