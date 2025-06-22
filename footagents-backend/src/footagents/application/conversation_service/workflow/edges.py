from typing import Literal
from langgraph.graph import END
from .state import FootAgentState


def should_summarize(state: FootAgentState) -> Literal["summarize_conversation_node", "__end__"]:
    """Decide whether we should branch to the summarization node."""
    if len(state["messages"]) > 10:
        return "summarize_conversation_node"
    return END 