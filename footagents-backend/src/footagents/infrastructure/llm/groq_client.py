import os
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import HumanMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()


def get_groq_client(temperature: float = 0.7, model: str = "llama-3.3-70b-versatile") -> ChatGroq:
    return ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model_name=model,
        temperature=temperature,
    )


def get_character_chain():
    model = get_groq_client()
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are {character_name}, the legendary football player. 

Your details:
- Position: {position}
- Era: {era}
- Personality: {perspective}
- Style: {style}

Rules:
- Stay in character
- Never mention you're an AI  
- Keep responses under 80 words
- Share football wisdom
- Be authentic to your personality
- If first interaction, introduce yourself briefly

{context}
{summary}"""),
        MessagesPlaceholder(variable_name="messages"),
    ])
    
    return prompt | model


def get_summary_chain(model_name: str = "llama-3.1-8b-instant"):
    model = get_groq_client(model=model_name)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Summarize this in under 50 words, keeping key details:"),
        ("human", "{text}"),
    ])
    
    return prompt | model 