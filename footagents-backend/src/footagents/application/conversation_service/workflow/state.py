from langgraph.graph import MessagesState

class FootAgentState(MessagesState):
    """State class for FootAgent conversation workflow."""
    
    character_context: str = ""
    character_name: str = ""
    character_position: str = ""
    character_era: str = ""
    character_perspective: str = ""
    character_style: str = ""
    summary: str = ""
    system_context: str = "" 