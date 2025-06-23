from typing import Literal
from langgraph.graph import END
from .state import FootAgentState


def tools_condition(state: FootAgentState) -> Literal["retrieve_philosopher_context", "connector_node"]:
    """Decide whether we should retrieve context using tools."""
    # Always retrieve context for the first interaction or when context is missing
    if not state.get("character_context") or len(state["messages"]) <= 1:
        return "retrieve_philosopher_context"
    return "connector_node"


def should_summarize(state: FootAgentState) -> Literal["summarize_conversation_node", "__end__"]:
    """Decide whether we should branch to the summarization node."""
    if len(state["messages"]) > 10:
        return "summarize_conversation_node"
    return "__end__"


def should_summarize_conversation(state: FootAgentState) -> Literal["summarize_conversation_node", "__end__"]:
    """Decide whether to summarize the conversation after connector node."""
    if len(state["messages"]) > 15:
        return "summarize_conversation_node"
    return "__end__" 