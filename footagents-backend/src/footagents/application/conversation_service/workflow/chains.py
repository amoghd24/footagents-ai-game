"""Chains module providing specialized LangChain pipelines for different conversation tasks."""

import os
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from dotenv import load_dotenv

from ....domain.prompts import FOOTBALL_CHARACTER_CARD, CONTEXT_SUMMARY_PROMPT, CONVERSATION_SUMMARY_PROMPT

load_dotenv()

# Model configurations
DEFAULT_MODEL = "llama-3.3-70b-versatile"
SUMMARY_MODEL = "llama-3.1-8b-instant"  # Faster model for summarization
DEFAULT_TEMPERATURE = 0.7
SUMMARY_TEMPERATURE = 0.3  # Lower for more consistent summaries


def get_chat_model(temperature: float = DEFAULT_TEMPERATURE, model_name: str = DEFAULT_MODEL) -> ChatGroq:
    """Create a ChatGroq model instance with specified configuration."""
    return ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model_name=model_name,
        temperature=temperature,
    )


def get_character_response_chain():
    """Create the main conversation chain for football character responses."""
    model = get_chat_model()
    
    # Import tools here to avoid circular import
    try:
        from .tools import tools
        model = model.bind_tools(tools)  # Enable tool usage for RAG
    except ImportError:
        pass  # Continue without tools if not available
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", FOOTBALL_CHARACTER_CARD),
        MessagesPlaceholder(variable_name="messages"),
    ])
    
    return prompt | model


def get_conversation_summary_chain(existing_summary: str = ""):
    """Create a chain for conversation summarization with memory management."""
    model = get_chat_model(model_name=SUMMARY_MODEL, temperature=SUMMARY_TEMPERATURE)
    
    # Choose prompt based on whether we're extending existing summary
    if existing_summary:
        summary_prompt = """Update this conversation summary with new information:

Existing summary: {existing_summary}

New conversation to integrate:
{messages}

Provide an updated summary focusing on key topics and advice given."""
    else:
        summary_prompt = CONVERSATION_SUMMARY_PROMPT
    
    prompt = ChatPromptTemplate.from_messages([
        ("human", summary_prompt),
    ])
    
    return prompt | model


def get_context_summary_chain():
    """Create a chain for summarizing retrieved context efficiently."""
    model = get_chat_model(model_name=SUMMARY_MODEL, temperature=SUMMARY_TEMPERATURE)
    
    prompt = ChatPromptTemplate.from_messages([
        ("human", CONTEXT_SUMMARY_PROMPT),
    ])
    
    return prompt | model


def get_simple_summary_chain():
    """Create a simple summary chain for general text summarization."""
    model = get_chat_model(
        model_name=SUMMARY_MODEL,
        temperature=SUMMARY_TEMPERATURE
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Summarize this in under 50 words, keeping key details:"),
        ("human", "{text}"),
    ])
    
    return prompt | model 