"""Tools module providing language model chains and retriever tools for the workflow."""

from langchain.tools.retriever import create_retriever_tool
from ....infrastructure.llm.groq_client import (
    get_character_chain as _get_character_chain,
    get_summary_chain as _get_summary_chain,
)
from ....infrastructure.rag.retrievers import get_retriever

# Expose the tool functions expected by nodes
get_character_chain = _get_character_chain
get_summary_chain = _get_summary_chain

# Create retriever and retriever tool as shown in lesson 1
retriever = get_retriever(
    embedding_model_id="sentence-transformers/all-MiniLM-L6-v2",
    k=5,
    device="cpu"
)

retriever_tool = create_retriever_tool(
    retriever,
    "retrieve_philosopher_context",
    "Search and return information about a specific philosopher.",
)

tools = [retriever_tool] 