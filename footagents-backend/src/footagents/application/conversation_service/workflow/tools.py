"""Tools module providing language model chains and retriever tools for the workflow."""

from langchain.tools.retriever import create_retriever_tool
from ....infrastructure.rag.retrievers import get_retriever

# Create retriever and retriever tool as shown in lesson 1
retriever = get_retriever(
    embedding_model_id="sentence-transformers/all-MiniLM-L6-v2",
    k=5,
    device="cpu"
)

retriever_tool = create_retriever_tool(
    retriever,
    "retrieve_player_context",
    "Search and return information about a specific football player.",
)

tools = [retriever_tool] 