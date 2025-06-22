from langgraph.graph import StateGraph, START, END
from .state import FootAgentState
from .nodes import conversation_node, summarize_conversation_node
from .edges import should_summarize


def create_footagent_workflow():
    """Build and compile the FootAgent conversation workflow graph."""
    workflow = StateGraph(FootAgentState)
    # Add nodes
    workflow.add_node("conversation_node", conversation_node)
    workflow.add_node("summarize_conversation_node", summarize_conversation_node)

    # Define edges
    workflow.add_edge(START, "conversation_node")
    workflow.add_conditional_edges(
        "conversation_node",
        should_summarize,
        {
            "summarize_conversation_node": "summarize_conversation_node",
            "__end__": END
        }
    )
    workflow.add_edge("summarize_conversation_node", END)

    return workflow.compile() 