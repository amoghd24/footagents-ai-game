from langgraph.graph import StateGraph, START, END
from .state import FootAgentState
from .nodes import (
    conversation_node, 
    retrieve_philosopher_context, 
    summarize_conversation_node,
    summarize_context_node,
    connector_node
)
from .edges import should_summarize_conversation


def create_workflow_graph():
    """Build and compile the FootAgent conversation workflow graph with 7 nodes."""
    graph_builder = StateGraph(FootAgentState)
    
    # Add all nodes
    graph_builder.add_node("conversation_node", conversation_node)
    graph_builder.add_node("retrieve_philosopher_context", retrieve_philosopher_context)
    graph_builder.add_node("summarize_conversation_node", summarize_conversation_node)
    graph_builder.add_node("summarize_context_node", summarize_context_node)
    graph_builder.add_node("connector_node", connector_node)
    
    # Define the flow: START -> retrieve context -> summarize context -> conversation -> connector -> END
    graph_builder.add_edge(START, "retrieve_philosopher_context")
    graph_builder.add_edge("retrieve_philosopher_context", "summarize_context_node")
    graph_builder.add_edge("summarize_context_node", "conversation_node")
    graph_builder.add_edge("conversation_node", "connector_node")
    graph_builder.add_conditional_edges(
        "connector_node", 
        should_summarize_conversation,
        {
            "summarize_conversation_node": "summarize_conversation_node",
            "__end__": END
        }
    )
    graph_builder.add_edge("summarize_conversation_node", END)
    
    return graph_builder


def create_footagent_workflow():
    """Build and compile the FootAgent conversation workflow graph."""
    graph_builder = create_workflow_graph()
    return graph_builder.compile() 