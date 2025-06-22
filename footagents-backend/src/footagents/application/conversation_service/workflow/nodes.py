from langgraph.graph.message import RemoveMessage
from .state import FootAgentState
from .tools import get_character_chain, get_summary_chain

async def conversation_node(state: FootAgentState):
    """Invoke the character chain to generate a response."""
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
    """Summarize the conversation and remove old messages."""
    summary_chain = get_summary_chain()
    conversation_text = "\n".join([
        f"{msg.type}: {msg.content}" for msg in state["messages"]
    ])
    response = await summary_chain.ainvoke({
        "text": f"Conversation with {state['character_name']}:\n{conversation_text}"
    })
    delete_messages = [RemoveMessage(id=msg.id) for msg in state["messages"][:-5]]
    return {
        "summary": response.content,
        "messages": delete_messages
    } 