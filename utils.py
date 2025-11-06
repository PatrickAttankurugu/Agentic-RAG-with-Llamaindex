# TODO: abstract all of this into a function that takes in a PDF file name 

from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, SummaryIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.tools import FunctionTool, QueryEngineTool
from llama_index.core.vector_stores import MetadataFilters, FilterCondition
from typing import List, Optional


# def get_doc_tools(
#     file_path: str,
#     name: str,
# ) -> str:
#     """Get vector query and summary query tools from a document."""
    
#     # load documents
#     documents = SimpleDirectoryReader(input_files=[file_path]).load_data()
#     splitter = SentenceSplitter(chunk_size=1024)
#     nodes = splitter.get_nodes_from_documents(documents)
#     vector_index = VectorStoreIndex(nodes)

#     def vector_query(
#         query: str, 
#         filter_key_list: List[str],
#         filter_value_list: List[str]
#     ) -> str:
#         """Perform a vector search over an index.

#         query (str): the string query to be embedded.
#         filter_key_list (List[str]): A list of metadata filter field names
#             Must specify ['page_label'] or empty list. Please leave empty
#             if there are no explicit filters to specify.
#         filter_value_list (List[str]): List of metadata filter field values 
#             (corresponding to names specified in filter_key_list) 

#         """
#         metadata_dicts = [
#             {"key": k, "value": v} for k, v in zip(filter_key_list, filter_value_list)
#         ]

#         query_engine = vector_index.as_query_engine(
#             similarity_top_k=2,
#             filters=MetadataFilters.from_dicts(metadata_dicts)
#         )
#         response = query_engine.query(query)
#         return response

#     vector_query_tool = FunctionTool.from_defaults(
#         fn=vector_query,
#         name=f"vector_query_{name}"
#     )

#     summary_index = SummaryIndex(nodes)
#     summary_query_engine = summary_index.as_query_engine(
#         response_mode="tree_summarize",
#         use_async=True,
#     )
#     summary_tool = QueryEngineTool.from_defaults(
#         query_engine=summary_query_engine,
#         name=f"summary_query_{name}",
#         description=(
#             f"Useful for summarization questions related to {name}"
#         ),
#     )
#     return vector_query_tool, summary_tool



def get_doc_tools(
    file_path: str,
    name: str,
) -> str:
    """Get vector query and summary query tools from a document."""

    # load documents
    documents = SimpleDirectoryReader(input_files=[file_path]).load_data()
    splitter = SentenceSplitter(chunk_size=1024)
    nodes = splitter.get_nodes_from_documents(documents)
    vector_index = VectorStoreIndex(nodes)
    
    def vector_query(
        query: str, 
        page_numbers: Optional[List[str]] = None
    ) -> str:
        """Use to answer questions over a given paper.
    
        Useful if you have specific questions over the paper.
        Always leave page_numbers as None UNLESS there is a specific page you want to search for.
    
        Args:
            query (str): the string query to be embedded.
            page_numbers (Optional[List[str]]): Filter by set of pages. Leave as NONE 
                if we want to perform a vector search
                over all pages. Otherwise, filter by the set of specified pages.
        
        """
    
        page_numbers = page_numbers or []
        metadata_dicts = [
            {"key": "page_label", "value": p} for p in page_numbers
        ]
        
        query_engine = vector_index.as_query_engine(
            similarity_top_k=2,
            filters=MetadataFilters.from_dicts(
                metadata_dicts,
                condition=FilterCondition.OR
            )
        )
        response = query_engine.query(query)
        return response
        
    
    vector_query_tool = FunctionTool.from_defaults(
        name=f"vector_tool_{name}",
        fn=vector_query
    )
    
    summary_index = SummaryIndex(nodes)
    summary_query_engine = summary_index.as_query_engine(
        response_mode="tree_summarize",
        use_async=True,
    )
    summary_tool = QueryEngineTool.from_defaults(
        name=f"summary_tool_{name}",
        query_engine=summary_query_engine,
        description=(
            f"Useful for summarization questions related to {name}"
        ),
    )

    return vector_query_tool, summary_tool


def get_router_query_engine(file_path: str, llm=None, embed_model=None):
    """Get router query engine for a document.

    This creates a router that can intelligently choose between:
    - Summary mode: For high-level summarization questions
    - Vector mode: For specific detail retrieval

    Args:
        file_path (str): Path to the PDF file
        llm: Optional LLM instance (will use default if None)
        embed_model: Optional embedding model (will use default if None)

    Returns:
        RouterQueryEngine: A router query engine
    """
    from llama_index.core import SimpleDirectoryReader
    from llama_index.core.node_parser import SentenceSplitter
    from llama_index.core import SummaryIndex, VectorStoreIndex
    from llama_index.core.tools import QueryEngineTool
    from llama_index.core.query_engine.router_query_engine import RouterQueryEngine
    from llama_index.core.selectors import LLMSingleSelector
    from llama_index.core import Settings
    from pathlib import Path

    # Use provided models or defaults
    if llm:
        Settings.llm = llm
    if embed_model:
        Settings.embed_model = embed_model

    # Load documents
    documents = SimpleDirectoryReader(input_files=[file_path]).load_data()
    splitter = SentenceSplitter(chunk_size=1024)
    nodes = splitter.get_nodes_from_documents(documents)

    # Create indices
    summary_index = SummaryIndex(nodes)
    vector_index = VectorStoreIndex(nodes)

    # Create query engines
    summary_query_engine = summary_index.as_query_engine(
        response_mode="tree_summarize",
        use_async=True,
    )
    vector_query_engine = vector_index.as_query_engine()

    # Get document name
    doc_name = Path(file_path).stem

    # Create tools
    summary_tool = QueryEngineTool.from_defaults(
        query_engine=summary_query_engine,
        description=(
            f"Useful for summarization questions related to {doc_name}"
        ),
    )

    vector_tool = QueryEngineTool.from_defaults(
        query_engine=vector_query_engine,
        description=(
            f"Useful for retrieving specific context from the {doc_name} document."
        ),
    )

    # Create router query engine
    query_engine = RouterQueryEngine(
        selector=LLMSingleSelector.from_defaults(),
        query_engine_tools=[
            summary_tool,
            vector_tool,
        ],
        verbose=True
    )

    return query_engine