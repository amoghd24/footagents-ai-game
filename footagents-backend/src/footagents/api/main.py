from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
import uuid
import os
from dotenv import load_dotenv

from ..domain.models import ChatRequest, ChatResponse
from ..domain.character_factory import FootballLegendFactory
from ..application.conversation_service.workflow.service import get_character_response
from ..integrations.mongodb.connection import db_manager
from ..integrations.mongodb.repositories import conversation_repository, character_repository, chat_log_repository
from ..integrations.mongodb.models import ConversationDocument, ChatLogDocument

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await db_manager.connect()
    yield
    # Shutdown
    await db_manager.disconnect()


app = FastAPI(title="FootAgents API", version="1.0.0", lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "FootAgents API is running!"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}


@app.get("/characters")
async def get_characters():
    legends = FootballLegendFactory.get_available_legends()
    return {"characters": legends}


@app.get("/characters/{character_id}")
async def get_character(character_id: str):
    try:
        legend = FootballLegendFactory.get_legend(character_id)
        return legend.dict()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/chat", response_model=ChatResponse)
async def chat_with_character(request: ChatRequest):
    start_time = datetime.now()
    
    try:
        # Get or create conversation
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        # Get or create conversation from MongoDB
        conversation = await conversation_repository.find_by_conversation_id(conversation_id)
        
        if conversation is None:
            # Create new conversation
            # Get character information
            try:
                character_legend = FootballLegendFactory.get_legend(request.character_id)
            except ValueError:
                raise HTTPException(status_code=404, detail=f"Character {request.character_id} not found")
            
            # Create new conversation document
            conversation = ConversationDocument(
                conversation_id=conversation_id,
                character_id=request.character_id,
                messages=[],
                character_context="",
                character_name=character_legend.name,
                character_perspective=character_legend.perspective,
                character_style=character_legend.style,
                summary=""
            )
            conversation = await conversation_repository.create(conversation)
        
        # Get conversation history for the AI service
        conversation_history = conversation.messages
        
        # Get character response
        response_text, updated_state = await get_character_response(
            message=request.message,
            character_id=request.character_id,
            conversation_history=conversation_history,
            summary=conversation.summary
        )
        
        # Add user message to conversation
        await conversation_repository.add_message_to_conversation(
            conversation_id, "user", request.message
        )
        
        # Add assistant response to conversation
        await conversation_repository.add_message_to_conversation(
            conversation_id, "assistant", response_text
        )
        
        # Update conversation summary if provided
        if updated_state.get("summary"):
            await conversation_repository.update(
                str(conversation.id), 
                {"summary": updated_state["summary"]}
            )
        
        # Create chat response
        chat_response = ChatResponse(
            response=response_text,
            character_id=request.character_id,
            conversation_id=conversation_id,
            timestamp=datetime.now()
        )
        
        # Log the interaction for analytics
        response_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        chat_log = ChatLogDocument.from_chat_interaction(request, chat_response, response_time_ms)
        await chat_log_repository.create(chat_log)
        
        # Increment character conversation count
        await character_repository.increment_conversation_count(request.character_id)
        
        return chat_response
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get conversation details and history."""
    try:
        conversation = await conversation_repository.find_by_conversation_id(conversation_id)
        if conversation is None:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return {
            "conversation_id": conversation.conversation_id,
            "character_id": conversation.character_id,
            "character_name": conversation.character_name,
            "messages": conversation.messages,
            "summary": conversation.summary,
            "created_at": conversation.created_at,
            "updated_at": conversation.updated_at,
            "is_active": conversation.is_active
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation and mark it as inactive."""
    try:
        conversation = await conversation_repository.find_by_conversation_id(conversation_id)
        if conversation is None:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Mark conversation as inactive instead of deleting
        await conversation_repository.update(
            str(conversation.id), 
            {"is_active": False}
        )
        
        return {"message": "Conversation deleted", "conversation_id": conversation_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=True
    ) 