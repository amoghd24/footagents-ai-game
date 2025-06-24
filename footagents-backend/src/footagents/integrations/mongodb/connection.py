"""
MongoDB Connection Manager

This module provides a singleton connection manager for MongoDB using Motor async driver.
Ensures single connection instance across the application with proper error handling.
"""

import os
import asyncio
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)


class MongoDBConnectionManager:
    """
    Singleton MongoDB connection manager for async operations.
    
    This class ensures only one MongoDB connection instance exists throughout
    the application lifecycle, providing efficient resource management.
    """
    
    _instance: Optional['MongoDBConnectionManager'] = None
    _client: Optional[AsyncIOMotorClient] = None
    _database: Optional[AsyncIOMotorDatabase] = None
    _lock = asyncio.Lock()
    
    def __new__(cls) -> 'MongoDBConnectionManager':
        """Ensure only one instance exists (Singleton pattern)."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def connect(self) -> None:
        """
        Establish connection to MongoDB.
        
        Raises:
            ConnectionError: If unable to connect to MongoDB
            ValueError: If required environment variables are missing
        """
        async with self._lock:
            if self._client is not None:
                logger.info("MongoDB connection already established")
                return
                
            try:
                # Get configuration from environment
                connection_string = os.getenv("MONGODB_CONNECTION_STRING")
                database_name = os.getenv("DATABASE_NAME", "footagents_db")
                
                if not connection_string:
                    raise ValueError("MONGODB_CONNECTION_STRING environment variable is required")
                
                # Create MongoDB client
                self._client = AsyncIOMotorClient(connection_string)
                
                # Test connection
                await self._client.admin.command('ping')
                
                # Extract database name from connection string if it exists
                if "/footagents_db?" in connection_string:
                    actual_database_name = "footagents_db"
                elif "/" in connection_string and "?" in connection_string:
                    # Extract database name between the last "/" and "?"
                    start = connection_string.rfind("/") + 1
                    end = connection_string.find("?", start)
                    actual_database_name = connection_string[start:end] if end > start else database_name
                else:
                    actual_database_name = database_name
                
                logger.info(f"Connecting to MongoDB database: {actual_database_name}")
                
                # Get database
                self._database = self._client[actual_database_name]
                
                logger.info("✅ MongoDB connection established successfully")
                
            except Exception as e:
                logger.error(f"❌ Failed to connect to MongoDB: {str(e)}")
                await self.disconnect()
                raise ConnectionError(f"Failed to connect to MongoDB: {str(e)}")
    
    async def disconnect(self) -> None:
        """Close MongoDB connection and cleanup resources."""
        async with self._lock:
            if self._client:
                self._client.close()
                self._client = None
                self._database = None
                logger.info("MongoDB connection closed")
    
    @property
    def database(self) -> AsyncIOMotorDatabase:
        """
        Get the MongoDB database instance.
        
        Returns:
            AsyncIOMotorDatabase: The database instance
            
        Raises:
            ConnectionError: If not connected to MongoDB
        """
        if self._database is None:
            raise ConnectionError("Not connected to MongoDB. Call connect() first.")
        return self._database
    
    @property
    def is_connected(self) -> bool:
        """Check if connected to MongoDB."""
        return self._client is not None and self._database is not None
    
    async def health_check(self) -> bool:
        """
        Perform a health check on the MongoDB connection.
        
        Returns:
            bool: True if connection is healthy, False otherwise
        """
        try:
            if not self.is_connected:
                return False
            
            # Ping the database
            await self._client.admin.command('ping')
            return True
            
        except Exception as e:
            logger.error(f"MongoDB health check failed: {str(e)}")
            return False
    
    async def get_collection_names(self) -> list[str]:
        """
        Get list of all collection names in the database.
        
        Returns:
            list[str]: List of collection names
        """
        if not self.is_connected:
            await self.connect()
        
        return await self.database.list_collection_names()


# Global instance for easy access
db_manager = MongoDBConnectionManager() 