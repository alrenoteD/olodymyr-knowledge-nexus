
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Memory API for Olodymyr AI Assistant

This module provides a unified interface to Olodymyr's memory systems,
coordinating between ChromaDB for vector storage and Supabase for relational data.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class MemoryAPI:
    """
    Unified API for accessing and managing Olodymyr's memory systems.
    """
    
    def __init__(self, chroma_memory, supabase_store, config):
        """
        Initialize the Memory API.
        
        Args:
            chroma_memory: ChromaDB memory instance
            supabase_store: Supabase storage instance
            config: Configuration dictionary
        """
        self.chroma_memory = chroma_memory
        self.supabase_store = supabase_store
        self.config = config
        
        # Set up memory limits from config
        self.short_term_limit = config["memory"].get("short_term_limit", 10)
        self.working_memory_tokens = config["memory"].get("working_memory_tokens", 2000)
        self.chunk_size = config["memory"].get("max_learning_chunk_size", 500)
        
        logger.info("Memory API initialized")
    
    async def setup_memory_systems(self):
        """
        Set up and initialize memory systems.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Initialize ChromaDB
            await self.chroma_memory.initialize()
            
            # Initialize Supabase
            await self.supabase_store.initialize()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to set up memory systems: {e}")
            return False
    
    # Context management functions
    
    async def get_conversation_history(self, user_id: str, message_limit: int = None) -> List[Dict]:
        """
        Get conversation history for a user.
        
        Args:
            user_id: The user's ID
            message_limit: Maximum number of messages to retrieve (default: from config)
            
        Returns:
            List of message dictionaries
        """
        limit = message_limit or self.short_term_limit
        return await self.supabase_store.get_conversation_history(user_id, limit)
    
    async def add_message_to_history(self, user_id: str, role: str, content: str) -> bool:
        """
        Add a message to the conversation history.
        
        Args:
            user_id: The user's ID
            role: Message role ('user' or 'assistant')
            content: Message content
            
        Returns:
            True if successful, False otherwise
        """
        return await self.supabase_store.add_message_to_history(user_id, role, content)
    
    async def clear_conversation_history(self, user_id: str) -> bool:
        """
        Clear conversation history for a user.
        
        Args:
            user_id: The user's ID
            
        Returns:
            True if successful, False otherwise
        """
        return await self.supabase_store.clear_conversation_history(user_id)
    
    # Learning sessions functions
    
    async def create_learning_session(self, user_id: str, name: str, content: str, 
                                    description: str = None, source: str = None) -> str:
        """
        Create a new learning session.
        
        Args:
            user_id: The user's ID
            name: Session name
            content: Session content
            description: Optional description
            source: Optional source (like URL)
            
        Returns:
            Session ID if successful
        """
        try:
            # Store in Supabase first to get an ID
            session_id = await self.supabase_store.create_learning_session(
                user_id, name, content, description, source
            )
            
            # Process content for vector storage
            await self.process_and_store_vectors(session_id, content)
            
            return session_id
            
        except Exception as e:
            logger.error(f"Failed to create learning session: {e}")
            raise
    
    async def get_learning_session(self, user_id: str, name: str) -> Dict:
        """
        Get a learning session by name.
        
        Args:
            user_id: The user's ID
            name: Session name
            
        Returns:
            Session data or None if not found
        """
        return await self.supabase_store.get_learning_session_by_name(user_id, name)
    
    async def list_learning_sessions(self, user_id: str) -> List[Dict]:
        """
        List all learning sessions for a user.
        
        Args:
            user_id: The user's ID
            
        Returns:
            List of session metadata
        """
        return await self.supabase_store.list_learning_sessions(user_id)
    
    async def delete_learning_session(self, session_id: str) -> bool:
        """
        Delete a learning session.
        
        Args:
            session_id: Session ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Delete from vector store first
            await self.chroma_memory.delete_vectors(session_id)
            
            # Then delete from Supabase
            await self.supabase_store.delete_learning_session(session_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete learning session: {e}")
            return False
    
    # Vector memory functions
    
    async def process_and_store_vectors(self, session_id: str, content: str) -> bool:
        """
        Process content and store as vectors.
        
        Args:
            session_id: Session ID to associate with vectors
            content: Content to process and store
            
        Returns:
            True if successful
        """
        try:
            # Chunk the content
            chunks = self._chunk_text(content, self.chunk_size)
            
            # Store each chunk
            for i, chunk in enumerate(chunks):
                metadata = {
                    "session_id": session_id,
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                }
                
                await self.chroma_memory.add_vector(
                    id=f"{session_id}_{i}",
                    text=chunk,
                    metadata=metadata
                )
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to process and store vectors: {e}")
            raise
    
    async def search_vectors(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Search for relevant vectors based on a query.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of relevant text chunks with metadata
        """
        return await self.chroma_memory.search(query, limit)
    
    async def get_relevant_memories(self, user_id: str, query: str, limit: int = 3) -> List[Dict]:
        """
        Get relevant memories for a query.
        
        Args:
            user_id: The user's ID
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of relevant memories with session metadata
        """
        try:
            # Search vector store
            vector_results = await self.chroma_memory.search(query, limit)
            
            if not vector_results:
                return []
            
            # Get unique session IDs
            session_ids = set()
            for result in vector_results:
                if "metadata" in result and "session_id" in result["metadata"]:
                    session_ids.add(result["metadata"]["session_id"])
            
            # Get session metadata
            results_with_metadata = []
            for result in vector_results:
                session_id = result["metadata"]["session_id"]
                session = await self.supabase_store.get_learning_session(session_id)
                
                if session:
                    results_with_metadata.append({
                        "content": result["text"],
                        "session_name": session.get("name", "Unknown"),
                        "relevance": result.get("distance", 1.0),
                        "session_id": session_id
                    })
            
            return results_with_metadata
            
        except Exception as e:
            logger.error(f"Failed to get relevant memories: {e}")
            return []
    
    # User preferences
    
    async def get_user_preferences(self, user_id: str) -> Dict:
        """
        Get user preferences.
        
        Args:
            user_id: The user's ID
            
        Returns:
            User preference dictionary
        """
        return await self.supabase_store.get_user_preferences(user_id)
    
    async def update_user_preferences(self, user_id: str, preferences: Dict) -> bool:
        """
        Update user preferences.
        
        Args:
            user_id: The user's ID
            preferences: Preference dictionary
            
        Returns:
            True if successful, False otherwise
        """
        return await self.supabase_store.update_user_preferences(user_id, preferences)
    
    # Utility functions
    
    def _chunk_text(self, text: str, chunk_size: int) -> List[str]:
        """
        Split text into chunks of approximately equal size.
        
        Args:
            text: Text to split
            chunk_size: Approximate chunk size in characters
            
        Returns:
            List of text chunks
        """
        # Simple implementation - split by paragraphs first, then by sentences if needed
        paragraphs = text.split("\n\n")
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) <= chunk_size:
                current_chunk += paragraph + "\n\n"
            else:
                # If current chunk is not empty, add it to chunks
                if current_chunk:
                    chunks.append(current_chunk.strip())
                
                # If paragraph is larger than chunk_size, split it further
                if len(paragraph) > chunk_size:
                    sentences = paragraph.split(". ")
                    current_chunk = ""
                    
                    for sentence in sentences:
                        if len(current_chunk) + len(sentence) <= chunk_size:
                            current_chunk += sentence + ". "
                        else:
                            if current_chunk:
                                chunks.append(current_chunk.strip())
                            current_chunk = sentence + ". "
                else:
                    current_chunk = paragraph + "\n\n"
        
        # Add the last chunk if not empty
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks


async def setup_memory_systems(config):
    """
    Set up and configure memory systems.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Configured MemoryAPI instance
    """
    # Import here to avoid circular imports
    from memory.chroma_memory import ChromaMemory
    from memory.supabase_store import SupabaseStore
    
    # Set up ChromaDB
    chroma_memory = ChromaMemory(config)
    
    # Set up Supabase
    supabase_store = SupabaseStore(config)
    
    # Create Memory API
    memory_api = MemoryAPI(chroma_memory, supabase_store, config)
    
    # Initialize memory systems
    await memory_api.setup_memory_systems()
    
    return memory_api
