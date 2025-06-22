from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.schema import HumanMessage, AIMessage
from langgraph.graph.message import RemoveMessage
from typing import Annotated, Literal
import uuid

from ...infrastructure.llm.groq_client import get_character_chain, get_summary_chain
from ...domain.character_factory import FootballLegendFactory


class FootAgentState(MessagesState):
    character_context: str = ""
    character_name: str = ""
    character_position: str = ""
    character_era: str = ""
    character_perspective: str = ""
    character_style: str = ""
    summary: str = ""


async def conversation_node(state: FootAgentState):
    chain = get_character_chain()
    
    response = await chain.ainvoke({
        "character_name": state["character_name"],
        "position": state["character_position"], 
        "era": state["character_era"],
        "perspective": state["character_perspective"],
        "style": state["character_style"],
        "context": state.get("character_context", ""),
        "summary": state.get("summary", ""),
        "messages": state["messages"]
    })
    
    return {"messages": [response]}


async def summarize_conversation_node(state: FootAgentState):
    summary_chain = get_summary_chain()
    
    # Get conversation text
    conversation_text = "\n".join([
        f"{msg.type}: {msg.content}" for msg in state["messages"]
    ])
    
    response = await summary_chain.ainvoke({
        "text": f"Conversation with {state['character_name']}:\n{conversation_text}"
    })
    
    # Keep only last 5 messages
    delete_messages = [
        RemoveMessage(id=msg.id) for msg in state["messages"][:-5]
    ]
    
    return {
        "summary": response.content,
        "messages": delete_messages
    }


def should_summarize(state: FootAgentState) -> Literal["summarize_conversation_node", "__end__"]:
    if len(state["messages"]) > 10:
        return "summarize_conversation_node"
    return END


def create_footagent_workflow():
    workflow = StateGraph(FootAgentState)
    
    # Add nodes
    workflow.add_node("conversation_node", conversation_node)
    workflow.add_node("summarize_conversation_node", summarize_conversation_node)
    
    # Add edges
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


async def get_character_response(
    message: str,
    character_id: str,
    conversation_history: list = None,
    summary: str = ""
) -> tuple[str, FootAgentState]:
    
    # Get character details
    legend = FootballLegendFactory.get_legend(character_id)
    
    # Prepare messages
    messages = conversation_history or []
    messages.append(HumanMessage(content=message))
    
    # Create workflow
    workflow = create_footagent_workflow()
    
    # Run workflow
    result = await workflow.ainvoke({
        "messages": messages,
        "character_name": legend.name,
        "character_position": legend.position,
        "character_era": legend.era, 
        "character_perspective": legend.perspective,
        "character_style": legend.style,
        "summary": summary
    })
    
    # Get response
    last_message = result["messages"][-1]
    response_text = last_message.content if hasattr(last_message, 'content') else str(last_message)
    
    return response_text, result 