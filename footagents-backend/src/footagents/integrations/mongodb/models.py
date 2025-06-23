"""
MongoDB Document Models

This module defines MongoDB document schemas that extend the domain models
with database-specific functionality like ObjectId handling and serialization.
"""

from typing import Optional, List, Any, Dict
from datetime import datetime
from pydantic import BaseModel, Field
from bson import ObjectId

from ...domain.models import FootballLegend, ConversationState, ChatRequest, ChatResponse


class PyObjectId(ObjectId):
    """Custom ObjectId class for Pydantic compatibility."""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v, _info=None):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)
    
    @classmethod
    def __get_pydantic_json_schema__(cls, _core_schema, handler):
        return {'type': 'string'}


class MongoBaseDocument(BaseModel):
    """
    Base document class for MongoDB documents with common fields.
    
    Provides standard fields like id, created_at, and updated_at that all
    MongoDB documents should have.
    """
    
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert document to dictionary for MongoDB operations."""
        return self.dict(by_alias=True, exclude_unset=True)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create document instance from dictionary."""
        return cls(**data)


class ConversationDocument(MongoBaseDocument):
    """
    MongoDB document for storing conversations.
    
    Extends the domain ConversationState with MongoDB-specific fields
    and functionality for persistent storage.
    """
    
    conversation_id: str = Field(..., description="Unique conversation identifier")
    character_id: str = Field(..., description="ID of the character in conversation")
    messages: List[Dict[str, Any]] = Field(default_factory=list, description="Conversation messages")
    character_context: str = Field(default="", description="Character context information")
    character_name: str = Field(..., description="Name of the character")
    character_perspective: str = Field(default="", description="Character's perspective")
    character_style: str = Field(default="", description="Character's communication style")
    summary: str = Field(default="", description="Conversation summary")
    is_active: bool = Field(default=True, description="Whether conversation is active")
    
    @classmethod
    def from_conversation_state(cls, state: ConversationState, conversation_id: str, character_id: str):
        """Create ConversationDocument from ConversationState domain model."""
        return cls(
            conversation_id=conversation_id,
            character_id=character_id,
            messages=state.messages,
            character_context=state.character_context,
            character_name=state.character_name,
            character_perspective=state.character_perspective,
            character_style=state.character_style,
            summary=state.summary
        )
    
    def to_conversation_state(self) -> ConversationState:
        """Convert to domain ConversationState model."""
        return ConversationState(
            messages=self.messages,
            character_context=self.character_context,
            character_name=self.character_name,
            character_perspective=self.character_perspective,
            character_style=self.character_style,
            summary=self.summary
        )
    
    def add_message(self, role: str, content: str, timestamp: Optional[datetime] = None) -> None:
        """Add a message to the conversation."""
        if timestamp is None:
            timestamp = datetime.utcnow()
            
        message = {
            "role": role,
            "content": content,
            "timestamp": timestamp
        }
        self.messages.append(message)
        self.updated_at = datetime.utcnow()


class CharacterDocument(MongoBaseDocument):
    """
    MongoDB document for storing football legend character data.
    
    Extends the domain FootballLegend with MongoDB-specific fields
    for persistent character storage and retrieval.
    """
    
    character_id: str = Field(..., description="Unique character identifier")
    name: str = Field(..., description="Character name")
    position: str = Field(..., description="Football position")
    era: str = Field(..., description="Era when character played")
    perspective: str = Field(..., description="Character's perspective/personality")
    style: str = Field(..., description="Communication style")
    career_highlights: str = Field(..., description="Career achievements and highlights")
    is_active: bool = Field(default=True, description="Whether character is available")
    conversation_count: int = Field(default=0, description="Number of conversations")
    
    @classmethod
    def from_football_legend(cls, legend: FootballLegend):
        """Create CharacterDocument from FootballLegend domain model."""
        return cls(
            character_id=legend.id,
            name=legend.name,
            position=legend.position,
            era=legend.era,
            perspective=legend.perspective,
            style=legend.style,
            career_highlights=legend.career_highlights
        )
    
    def to_football_legend(self) -> FootballLegend:
        """Convert to domain FootballLegend model."""
        return FootballLegend(
            id=self.character_id,
            name=self.name,
            position=self.position,
            era=self.era,
            perspective=self.perspective,
            style=self.style,
            career_highlights=self.career_highlights
        )
    
    def increment_conversation_count(self) -> None:
        """Increment the conversation count for analytics."""
        self.conversation_count += 1
        self.updated_at = datetime.utcnow()


class ChatLogDocument(MongoBaseDocument):
    """
    MongoDB document for storing individual chat interactions.
    
    Useful for analytics, debugging, and detailed conversation tracking
    beyond the conversation-level storage.
    """
    
    conversation_id: str = Field(..., description="Associated conversation ID")
    character_id: str = Field(..., description="Character involved in chat")
    user_message: str = Field(..., description="User's message")
    assistant_response: str = Field(..., description="Assistant's response")
    response_time_ms: Optional[int] = Field(None, description="Response time in milliseconds")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @classmethod
    def from_chat_interaction(cls, request: ChatRequest, response: ChatResponse, response_time_ms: Optional[int] = None):
        """Create ChatLogDocument from chat request and response."""
        return cls(
            conversation_id=response.conversation_id,
            character_id=request.character_id,
            user_message=request.message,
            assistant_response=response.response,
            response_time_ms=response_time_ms,
            metadata={
                "request_timestamp": datetime.utcnow(),
                "response_timestamp": response.timestamp
            }
        ) 