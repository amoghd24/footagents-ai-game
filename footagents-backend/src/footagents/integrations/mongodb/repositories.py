"""
MongoDB Repository Pattern Implementation

This module implements the Repository pattern for clean data access layer.
Provides generic base repository and specific repositories for different entities.
"""

import logging
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, Type, TypeVar, Generic
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection

from .connection import db_manager
from .models import (
    MongoBaseDocument, 
    ConversationDocument, 
    CharacterDocument, 
    ChatLogDocument
)

logger = logging.getLogger(__name__)

# Generic type for documents
T = TypeVar('T', bound=MongoBaseDocument)


class BaseRepository(Generic[T], ABC):
    """
    Abstract base repository providing common CRUD operations.
    
    This class implements the Repository pattern with generic operations
    that can be inherited by specific entity repositories.
    """
    
    def __init__(self, collection_name: str, document_class: Type[T]):
        self.collection_name = collection_name
        self.document_class = document_class
        self._collection: Optional[AsyncIOMotorCollection] = None
    
    @property
    async def collection(self) -> AsyncIOMotorCollection:
        """Get the MongoDB collection, ensuring connection is established."""
        if self._collection is None:
            if not db_manager.is_connected:
                await db_manager.connect()
            self._collection = db_manager.database[self.collection_name]
        return self._collection
    
    async def create(self, document: T) -> T:
        """
        Create a new document in the collection.
        
        Args:
            document: The document to create
            
        Returns:
            The created document with updated fields
        """
        try:
            collection = await self.collection
            document.created_at = datetime.utcnow()
            document.updated_at = datetime.utcnow()
            
            result = await collection.insert_one(document.to_dict())
            document.id = result.inserted_id
            
            logger.info(f"Created {self.document_class.__name__} with ID: {result.inserted_id}")
            return document
            
        except Exception as e:
            logger.error(f"Error creating {self.document_class.__name__}: {str(e)}")
            raise
    
    async def find_by_id(self, document_id: str) -> Optional[T]:
        """
        Find a document by its ID.
        
        Args:
            document_id: The document ID to search for
            
        Returns:
            The document if found, None otherwise
        """
        try:
            collection = await self.collection
            
            # Try both string ID and ObjectId
            query = {"$or": [
                {"_id": ObjectId(document_id) if ObjectId.is_valid(document_id) else None},
                {"_id": document_id}
            ]}
            
            data = await collection.find_one(query)
            if data:
                return self.document_class.from_dict(data)
            return None
            
        except Exception as e:
            logger.error(f"Error finding {self.document_class.__name__} by ID {document_id}: {str(e)}")
            return None
    
    async def find_one(self, query: Dict[str, Any]) -> Optional[T]:
        """
        Find a single document matching the query.
        
        Args:
            query: MongoDB query dictionary
            
        Returns:
            The document if found, None otherwise
        """
        try:
            collection = await self.collection
            data = await collection.find_one(query)
            if data:
                return self.document_class.from_dict(data)
            return None
            
        except Exception as e:
            logger.error(f"Error finding {self.document_class.__name__}: {str(e)}")
            return None
    
    async def find_many(self, query: Dict[str, Any], limit: Optional[int] = None, skip: Optional[int] = None) -> List[T]:
        """
        Find multiple documents matching the query.
        
        Args:
            query: MongoDB query dictionary
            limit: Maximum number of documents to return
            skip: Number of documents to skip
            
        Returns:
            List of matching documents
        """
        try:
            collection = await self.collection
            cursor = collection.find(query)
            
            if skip:
                cursor = cursor.skip(skip)
            if limit:
                cursor = cursor.limit(limit)
                
            documents = []
            async for data in cursor:
                documents.append(self.document_class.from_dict(data))
                
            return documents
            
        except Exception as e:
            logger.error(f"Error finding {self.document_class.__name__} documents: {str(e)}")
            return []
    
    async def update(self, document_id: str, update_data: Dict[str, Any]) -> Optional[T]:
        """
        Update a document by ID.
        
        Args:
            document_id: The document ID to update
            update_data: Dictionary of fields to update
            
        Returns:
            The updated document if successful, None otherwise
        """
        try:
            collection = await self.collection
            update_data["updated_at"] = datetime.utcnow()
            
            query = {"$or": [
                {"_id": ObjectId(document_id) if ObjectId.is_valid(document_id) else None},
                {"_id": document_id}
            ]}
            
            result = await collection.update_one(query, {"$set": update_data})
            
            if result.modified_count > 0:
                return await self.find_by_id(document_id)
            return None
            
        except Exception as e:
            logger.error(f"Error updating {self.document_class.__name__} {document_id}: {str(e)}")
            return None
    
    async def delete(self, document_id: str) -> bool:
        """
        Delete a document by ID.
        
        Args:
            document_id: The document ID to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            collection = await self.collection
            
            query = {"$or": [
                {"_id": ObjectId(document_id) if ObjectId.is_valid(document_id) else None},
                {"_id": document_id}
            ]}
            
            result = await collection.delete_one(query)
            success = result.deleted_count > 0
            
            if success:
                logger.info(f"Deleted {self.document_class.__name__} with ID: {document_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting {self.document_class.__name__} {document_id}: {str(e)}")
            return False
    
    async def count(self, query: Dict[str, Any] = None) -> int:
        """
        Count documents matching the query.
        
        Args:
            query: MongoDB query dictionary (empty dict counts all)
            
        Returns:
            Number of matching documents
        """
        try:
            collection = await self.collection
            return await collection.count_documents(query or {})
            
        except Exception as e:
            logger.error(f"Error counting {self.document_class.__name__} documents: {str(e)}")
            return 0


class ConversationRepository(BaseRepository[ConversationDocument]):
    """Repository for conversation documents with specific business methods."""
    
    def __init__(self):
        super().__init__("conversations", ConversationDocument)
    
    async def find_by_conversation_id(self, conversation_id: str) -> Optional[ConversationDocument]:
        """Find conversation by conversation_id field."""
        return await self.find_one({"conversation_id": conversation_id})
    
    async def find_by_character_id(self, character_id: str, limit: int = 10) -> List[ConversationDocument]:
        """Find conversations for a specific character."""
        return await self.find_many(
            {"character_id": character_id, "is_active": True}, 
            limit=limit
        )
    
    async def add_message_to_conversation(self, conversation_id: str, role: str, content: str) -> Optional[ConversationDocument]:
        """Add a message to an existing conversation."""
        conversation = await self.find_by_conversation_id(conversation_id)
        if conversation:
            conversation.add_message(role, content)
            return await self.update(str(conversation.id), conversation.to_dict())
        return None
    
    async def get_active_conversations(self, limit: int = 50) -> List[ConversationDocument]:
        """Get all active conversations."""
        return await self.find_many({"is_active": True}, limit=limit)


class CharacterRepository(BaseRepository[CharacterDocument]):
    """Repository for character documents with specific business methods."""
    
    def __init__(self):
        super().__init__("characters", CharacterDocument)
    
    async def find_by_character_id(self, character_id: str) -> Optional[CharacterDocument]:
        """Find character by character_id field."""
        return await self.find_one({"character_id": character_id})
    
    async def get_active_characters(self) -> List[CharacterDocument]:
        """Get all active characters."""
        return await self.find_many({"is_active": True})
    
    async def increment_conversation_count(self, character_id: str) -> Optional[CharacterDocument]:
        """Increment conversation count for a character."""
        character = await self.find_by_character_id(character_id)
        if character:
            character.increment_conversation_count()
            return await self.update(str(character.id), character.to_dict())
        return None
    
    async def get_popular_characters(self, limit: int = 10) -> List[CharacterDocument]:
        """Get characters ordered by conversation count."""
        try:
            collection = await self.collection
            cursor = collection.find({"is_active": True}).sort("conversation_count", -1).limit(limit)
            
            characters = []
            async for data in cursor:
                characters.append(self.document_class.from_dict(data))
                
            return characters
            
        except Exception as e:
            logger.error(f"Error getting popular characters: {str(e)}")
            return []


class ChatLogRepository(BaseRepository[ChatLogDocument]):
    """Repository for chat log documents with analytics methods."""
    
    def __init__(self):
        super().__init__("chat_logs", ChatLogDocument)
    
    async def find_by_conversation_id(self, conversation_id: str) -> List[ChatLogDocument]:
        """Find all chat logs for a conversation."""
        return await self.find_many({"conversation_id": conversation_id})
    
    async def get_recent_chats(self, limit: int = 100) -> List[ChatLogDocument]:
        """Get recent chat interactions."""
        try:
            collection = await self.collection
            cursor = collection.find({}).sort("created_at", -1).limit(limit)
            
            chats = []
            async for data in cursor:
                chats.append(self.document_class.from_dict(data))
                
            return chats
            
        except Exception as e:
            logger.error(f"Error getting recent chats: {str(e)}")
            return []
    
    async def get_average_response_time(self, character_id: Optional[str] = None) -> float:
        """Get average response time, optionally filtered by character."""
        try:
            collection = await self.collection
            
            match_stage = {"response_time_ms": {"$ne": None}}
            if character_id:
                match_stage["character_id"] = character_id
            
            pipeline = [
                {"$match": match_stage},
                {"$group": {"_id": None, "avg_response_time": {"$avg": "$response_time_ms"}}}
            ]
            
            result = await collection.aggregate(pipeline).to_list(length=1)
            if result:
                return result[0]["avg_response_time"]
            return 0.0
            
        except Exception as e:
            logger.error(f"Error calculating average response time: {str(e)}")
            return 0.0


# Repository instances for easy access
conversation_repository = ConversationRepository()
character_repository = CharacterRepository()
chat_log_repository = ChatLogRepository() 