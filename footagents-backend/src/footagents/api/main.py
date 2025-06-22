from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uuid
import os
from dotenv import load_dotenv

from ..domain.models import ChatRequest, ChatResponse
from ..domain.character_factory import FootballLegendFactory
from ..application.conversation_service.workflow import get_character_response

load_dotenv()

app = FastAPI(title="FootAgents API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for conversations (replace with database later)
conversations = {}


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
    try:
        # Get or create conversation
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        # Get conversation history
        conversation_history = conversations.get(conversation_id, [])
        
        # Get character response
        response_text, updated_state = await get_character_response(
            message=request.message,
            character_id=request.character_id,
            conversation_history=conversation_history,
            summary=""
        )
        
        # Store updated conversation
        conversations[conversation_id] = updated_state["messages"]
        
        return ChatResponse(
            response=response_text,
            character_id=request.character_id,
            conversation_id=conversation_id,
            timestamp=datetime.now()
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    if conversation_id in conversations:
        del conversations[conversation_id]
        return {"message": "Conversation deleted"}
    raise HTTPException(status_code=404, detail="Conversation not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=True
    ) 