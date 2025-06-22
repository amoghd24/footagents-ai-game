from langchain.schema import HumanMessage
from ....domain.character_factory import FootballLegendFactory
from .graph import create_footagent_workflow
from .state import FootAgentState


async def get_character_response(
    message: str,
    character_id: str,
    conversation_history: list = None,
    summary: str = ""
) -> tuple[str, FootAgentState]:
    """Handle conversation by invoking the compiled workflow graph."""
    # Get character details
    legend = FootballLegendFactory.get_legend(character_id)

    # Prepare messages
    messages = conversation_history or []
    messages.append(HumanMessage(content=message))

    # Create and run the workflow
    workflow = create_footagent_workflow()
    result = await workflow.ainvoke({
        "messages": messages,
        "character_name": legend.name,
        "character_position": legend.position,
        "character_era": legend.era,
        "character_perspective": legend.perspective,
        "character_style": legend.style,
        "summary": summary
    })

    # Extract response
    last_message = result["messages"][-1]
    response_text = last_message.content if hasattr(last_message, 'content') else str(last_message)

    return response_text, result 