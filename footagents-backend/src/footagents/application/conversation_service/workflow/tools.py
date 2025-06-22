"""Tools module providing language model chains for the workflow."""

from ....infrastructure.llm.groq_client import (
    get_character_chain as _get_character_chain,
    get_summary_chain as _get_summary_chain,
)

# Expose the tool functions expected by nodes
get_character_chain = _get_character_chain
get_summary_chain = _get_summary_chain 