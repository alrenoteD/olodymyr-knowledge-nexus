
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Learning Engine for Olodymyr AI Assistant

This module manages the learning and memory recall capabilities.
"""

import logging
import asyncio
from typing import List, Dict, Any
import uuid

logger = logging.getLogger(__name__)

class LearningEngine:
    """
    Engine for managing learning and memory operations.
    """
    
    def __init__(self, config, memory_api, llm_client):
        """
        Initialize the Learning Engine.
        
        Args:
            config: Configuration dictionary
            memory_api: Memory API instance
            llm_client: LLM client instance
        """
        self.config = config
        self.memory_api = memory_api
        self.llm_client = llm_client
        
        logger.info("Learning Engine initialized")
    
    async def create_learning_session(self, user_id, name, content, description=None, source=None):
        """
        Create a new learning session.
        
        Args:
            user_id: User ID
            name: Session name
            content: Content to learn
            description: Optional description
            source: Optional source (like URL)
            
        Returns:
            Session ID if successful
        """
        try:
            # Create learning session in memory API
            session_id = await self.memory_api.create_learning_session(
                user_id=user_id,
                name=name,
                content=content,
                description=description,
                source=source
            )
            
            logger.info(f"Created learning session '{name}' for user {user_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Error creating learning session: {e}")
            raise
    
    async def get_learning_session(self, user_id, name):
        """
        Get a learning session by name.
        
        Args:
            user_id: User ID
            name: Session name
            
        Returns:
            Session data dictionary or None if not found
        """
        try:
            # Get learning session from memory API
            session = await self.memory_api.get_learning_session(user_id, name)
            return session
            
        except Exception as e:
            logger.error(f"Error retrieving learning session: {e}")
            return None
    
    async def list_learning_sessions(self, user_id):
        """
        List all learning sessions for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of session metadata
        """
        try:
            # List learning sessions from memory API
            sessions = await self.memory_api.list_learning_sessions(user_id)
            return sessions
            
        except Exception as e:
            logger.error(f"Error listing learning sessions: {e}")
            return []
    
    async def delete_learning_session(self, user_id, name):
        """
        Delete a learning session by name.
        
        Args:
            user_id: User ID
            name: Session name
            
        Returns:
            True if successful
        """
        try:
            # Get session ID first
            session = await self.memory_api.get_learning_session(user_id, name)
            
            if not session:
                logger.warning(f"Learning session '{name}' not found for user {user_id}")
                return False
                
            # Delete session
            success = await self.memory_api.delete_learning_session(session["id"])
            return success
            
        except Exception as e:
            logger.error(f"Error deleting learning session: {e}")
            return False
    
    async def get_relevant_memories(self, user_id, query, limit=3):
        """
        Get memories relevant to a query.
        
        Args:
            user_id: User ID
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of relevant memories
        """
        try:
            # Get relevant memories from memory API
            memories = await self.memory_api.get_relevant_memories(user_id, query, limit)
            return memories
            
        except Exception as e:
            logger.error(f"Error retrieving relevant memories: {e}")
            return []
    
    async def generate_learning_response(self, content):
        """
        Generate a response confirming learning.
        
        Args:
            content: The content that was learned
            
        Returns:
            Confirmation message
        """
        # Generate a simple confirmation message
        from llms.prompts import LEARNING_SYNTHESIS_TEMPLATE
        
        prompt = LEARNING_SYNTHESIS_TEMPLATE.format(content=content[:200] + "..." if len(content) > 200 else content)
        
        try:
            response = await self.llm_client.generate_completion(prompt)
            return f"✅ I've learned this information! Here's my understanding:\n\n{response}"
            
        except Exception as e:
            logger.error(f"Error generating learning response: {e}")
            return "✅ I've learned and stored this information!"
