
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Context Manager for Olodymyr AI Assistant

This module manages conversation context and working memory.
"""

import logging
from typing import List, Dict, Any
import asyncio

logger = logging.getLogger(__name__)

class ContextManager:
    """
    Manager for conversation context and working memory.
    """
    
    def __init__(self, config, memory_api):
        """
        Initialize the Context Manager.
        
        Args:
            config: Configuration dictionary
            memory_api: Memory API instance
        """
        self.config = config
        self.memory_api = memory_api
        self.short_term_limit = config["memory"].get("short_term_limit", 10)
        
        logger.info(f"Context Manager initialized with short_term_limit: {self.short_term_limit}")
    
    async def get_context(self, user_id):
        """
        Get conversation context for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of conversation messages
        """
        try:
            # Get conversation history from memory API
            history = await self.memory_api.get_conversation_history(user_id, self.short_term_limit)
            return history
            
        except Exception as e:
            logger.error(f"Error retrieving context for user {user_id}: {e}")
            return []
    
    async def add_message(self, user_id, role, content):
        """
        Add a message to the conversation context.
        
        Args:
            user_id: User ID
            role: Message role ('user' or 'assistant')
            content: Message content
            
        Returns:
            True if successful
        """
        try:
            # Add message to history using memory API
            success = await self.memory_api.add_message_to_history(user_id, role, content)
            return success
            
        except Exception as e:
            logger.error(f"Error adding message to context for user {user_id}: {e}")
            return False
    
    async def clear_context(self, user_id):
        """
        Clear conversation context for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            True if successful
        """
        try:
            # Clear conversation history using memory API
            success = await self.memory_api.clear_conversation_history(user_id)
            return success
            
        except Exception as e:
            logger.error(f"Error clearing context for user {user_id}: {e}")
            return False
    
    async def get_token_count(self, text):
        """
        Get approximate token count for a text.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Approximate token count
        """
        # Simple approximation: 1 token ≈ 4 characters
        return len(text) // 4
    
    async def optimize_context(self, context, max_tokens):
        """
        Optimize context to fit within token limit.
        
        Args:
            context: List of conversation messages
            max_tokens: Maximum tokens allowed
            
        Returns:
            Optimized context
        """
        if not context:
            return []
            
        # Start with the most recent messages
        optimized = []
        current_tokens = 0
        
        # Process messages from most recent to oldest
        for message in reversed(context):
            content = message.get("content", "")
            role = message.get("role", "unknown")
            
            # Estimate tokens for this message
            message_tokens = await self.get_token_count(f"{role}: {content}")
            
            # If adding this message would exceed limit, stop
            if current_tokens + message_tokens > max_tokens:
                break
                
            # Add message and update token count
            optimized.insert(0, message)  # Insert at beginning to maintain chronological order
            current_tokens += message_tokens
        
        return optimized
