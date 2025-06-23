"""Retriever components for RAG functionality."""

import os
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain.schema import Document


def get_retriever(
    embedding_model_id: str = "sentence-transformers/all-MiniLM-L6-v2",
    k: int = 5,
    device: str = "cpu"
):
    """Create and return a retriever for football legend context."""
    
    # Initialize embeddings
    embeddings = HuggingFaceEmbeddings(
        model_name=embedding_model_id,
        model_kwargs={'device': device}
    )
    
    # Create some sample football legend knowledge
    # In a real implementation, this would load from a knowledge base
    football_knowledge = [
        Document(
            page_content="Diego Maradona was an Argentine professional footballer widely regarded as one of the greatest players in the history of the sport. He played as an attacking midfielder and forward, known for his incredible dribbling, vision, and ability to score spectacular goals.",
            metadata={"character": "maradona", "topic": "biography"}
        ),
        Document(
            page_content="Lionel Messi is an Argentine professional footballer who plays as a forward. He has won numerous Ballon d'Or awards and is considered one of the greatest players of all time, known for his speed, finishing, and playmaking abilities.",
            metadata={"character": "leomessi", "topic": "biography"}
        ),
        Document(
            page_content="Cristiano Ronaldo is a Portuguese professional footballer who plays as a forward. He is known for his incredible athleticism, goal-scoring ability, and has won multiple Champions League titles and Ballon d'Or awards.",
            metadata={"character": "cristianoronaldo", "topic": "biography"}
        ),
        Document(
            page_content="Kaká is a Brazilian former professional footballer who played as an attacking midfielder. He was known for his pace, technique, and ability to score from midfield. He won the Ballon d'Or in 2007.",
            metadata={"character": "kaka", "topic": "biography"}
        ),
        Document(
            page_content="Pep Guardiola is a Spanish professional football manager and former player. As a manager, he is known for his tactical innovation, particularly his implementation of tiki-taka playing style.",
            metadata={"character": "pepguardiola", "topic": "coaching"}
        ),
        Document(
            page_content="Sir Alex Ferguson is a Scottish former football manager who managed Manchester United for 26 years. He is considered one of the greatest managers in football history, known for his man-management skills and tactical acumen.",
            metadata={"character": "alexferguson", "topic": "coaching"}
        ),
        Document(
            page_content="Jürgen Klopp is a German professional football manager known for his energetic coaching style and his ability to develop young players. He has managed Liverpool and Borussia Dortmund with great success.",
            metadata={"character": "jurgenklopp", "topic": "coaching"}
        ),
        Document(
            page_content="Carlo Ancelotti is an Italian professional football manager known for his calm demeanor and tactical flexibility. He has won the Champions League multiple times as both a player and manager.",
            metadata={"character": "ancelotti", "topic": "coaching"}
        )
    ]
    
    # Create vector store
    vectorstore = Chroma.from_documents(
        documents=football_knowledge,
        embedding=embeddings,
        persist_directory="./chroma_db"
    )
    
    # Create and return retriever
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k}
    )
    
    return retriever 