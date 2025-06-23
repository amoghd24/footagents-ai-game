from langgraph.graph.message import RemoveMessage
from langchain.schema import HumanMessage, AIMessage
from .state import FootAgentState
from .tools import retriever_tool
from .chains import (
    get_character_response_chain,
    get_conversation_summary_chain,
    get_context_summary_chain
)

async def conversation_node(state: FootAgentState):
    """Invoke the character chain to generate a response."""
    chain = get_character_response_chain()
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

async def retrieve_philosopher_context(state: FootAgentState):
    """Retrieve relevant context about the football legend/philosopher."""
    # Get the last human message to understand what context to retrieve
    last_message = state["messages"][-1] if state["messages"] else ""
    query = f"{state['character_name']} {last_message.content if hasattr(last_message, 'content') else str(last_message)}"
    
    # Use the retriever tool to get context
    context_docs = await retriever_tool.ainvoke({"query": query})
    
    # Combine the retrieved context
    context = "\n".join([doc.page_content if hasattr(doc, 'page_content') else str(doc) for doc in context_docs])
    
    return {"character_context": context}

async def summarize_conversation_node(state: FootAgentState):
    """Summarize the conversation and remove old messages."""
    existing_summary = state.get("summary", "")
    summary_chain = get_conversation_summary_chain(existing_summary)
    
    # Format messages for summarization
    formatted_messages = "\n".join([
        f"{msg.type}: {msg.content}" for msg in state["messages"]
    ])
    
    # Use appropriate parameters based on chain type
    if existing_summary:
        response = await summary_chain.ainvoke({
            "character_name": state["character_name"],
            "existing_summary": existing_summary, 
            "messages": formatted_messages
        })
    else:
        response = await summary_chain.ainvoke({
            "character_name": state["character_name"],
            "messages": formatted_messages
        })
    
    delete_messages = [RemoveMessage(id=msg.id) for msg in state["messages"][:-5]]
    return {
        "summary": response.content,
        "messages": delete_messages
    }

async def summarize_context_node(state: FootAgentState):
    """Summarize the retrieved context for better processing."""
    if not state.get("character_context"):
        return {"character_context": ""}
    
    context_summary_chain = get_context_summary_chain()
    response = await context_summary_chain.ainvoke({
        "context": state["character_context"]
    })
    
    return {"character_context": response.content}

async def connector_node(state: FootAgentState):
    """Connector node to handle flow control and state management."""
    # This node can be used to prepare state for the next phase
    # or perform any necessary transformations
    
    # Add a system message to help guide the conversation
    system_context = f"You are {state['character_name']}, a {state['character_position']} from the {state['character_era']} era."
    if state.get("character_context"):
        system_context += f" Context: {state['character_context']}"
    
    return {
        "system_context": system_context
    }