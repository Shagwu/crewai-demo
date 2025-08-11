# tools/document_query_tool.py
from crewai_tools import BaseTool
from llama_index.core import StorageContext, load_index_from_storage

class LocalDocQueryTool(BaseTool):
    name = "Local Document Knowledge Search"
    description = "Searches indexed knowledge from local documents"

    def _run(self, query: str) -> str:
        storage_context = StorageContext.from_defaults(persist_dir="llamaindex/vector_store")
        index = load_index_from_storage(storage_context)
        query_engine = index.as_query_engine()
        response = query_engine.query(query)
        return str(response)