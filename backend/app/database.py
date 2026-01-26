"""
Study Buddy App - Database Connection Management

This module handles MongoDB database connections using Motor (async MongoDB driver).
Provides connection lifecycle management for the Study Buddy App with proper
error handling and connection testing.

Features:
- Async MongoDB connection using Motor
- Connection health checking with ping
- Graceful connection cleanup
- Centralized database instance management
- Logging for connection status monitoring

The database stores all study sessions, generated content, user data,
and medical study materials for the MBBS-focused Study Buddy App.

Author: Study Buddy Team
Created: January 2026
License: MIT
"""

from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class Database:
    """
    Database connection manager for MongoDB.
    
    Maintains a single async MongoDB client and database instance
    for use throughout the application lifecycle.
    
    Attributes:
        client: AsyncIOMotorClient instance for MongoDB connection
        database: Database instance for Study Buddy collections
    """
    client: AsyncIOMotorClient = None
    database = None

# Global database instance
db = Database()

async def connect_to_mongo():
    """
    Establish connection to MongoDB database.
    
    Creates an async MongoDB client connection and tests connectivity
    with a ping command. Sets up the database instance for use by
    the application.
    
    Raises:
        Exception: If connection fails or MongoDB is unreachable
        
    Example:
        >>> await connect_to_mongo()
        # Logs: "Connected to MongoDB successfully"
    """
    try:
        db.client = AsyncIOMotorClient(settings.mongodb_url)
        db.database = db.client[settings.database_name]
        
        # Test connection with ping command
        await db.client.admin.command('ping')
        logger.info("Connected to MongoDB successfully")
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise

async def close_mongo_connection():
    """
    Close the MongoDB database connection.
    
    Properly closes the MongoDB client connection to free resources
    and ensure clean application shutdown.
    
    Example:
        >>> await close_mongo_connection()
        # Connection closed gracefully
    """
    if db.client:
        db.client.close()
        logger.info("Disconnected from MongoDB")

def get_database():
    """Get database instance"""
    return db.database
