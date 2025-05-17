
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Personality Engine for Olodymyr AI Assistant

This module manages Olodymyr's personality, tone, and communication style.
"""

import logging
from typing import Dict, List, Any
from llms.prompts import (
    SYSTEM_PROMPT, 
    CONVERSATION_PROMPT_TEMPLATE,
    WELCOME_MESSAGE_TEMPLATE,
    HELP_MESSAGE
)

logger = logging.getLogger(__name__)

class PersonalityEngine:
    """
    Engine for managing Olodymyr's personality and communication style.
    """
    
    def __init__(self, config):
        """
        Initialize the Personality Engine.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.personality_config = config.get("personality", {})
        self.name = self.personality_config.get("name", "Olodymyr")
        self.persona = self.personality_config.get("persona", "friendly, helpful professor")
        self.tone = self.personality_config.get("tone", "warm and educational")
        self.emoji_level = self.personality_config.get("emoji_level", "moderate")
        self.verbosity = self.personality_config.get("verbosity", "medium")
        
        logger.info(f"Personality Engine initialized with persona: {self.persona}")
    
    def build_prompt(self, conversation_history=None, relevant_memories=None, user_message=None):
        """
        Build a prompt for the LLM.
        
        Args:
            conversation_history: List of conversation messages
            relevant_memories: List of relevant memory items
            user_message: Optional user message to append
            
        Returns:
            Formatted prompt string
        """
        # Start with system prompt
        system_prompt = self._customize_system_prompt()
        
        # Format conversation history
        conversation_str = ""
        if conversation_history:
            for message in conversation_history:
                role = message.get("role", "unknown")
                content = message.get("content", "")
                conversation_str += f"{role.capitalize()}: {content}\n\n"
        
        # Format relevant memories
        memories_str = ""
        if relevant_memories and len(relevant_memories) > 0:
            memories_str = "Here are some relevant pieces of information from my memory:\n\n"
            for i, memory in enumerate(relevant_memories):
                memories_str += f"Memory {i+1} (from '{memory.get('session_name', 'unknown')}'):\n{memory.get('content', '')}\n\n"
        else:
            memories_str = "I don't have any specific memories relevant to this query."
        
        # Get user preferences (placeholder for now)
        user_preferences = "No specific preferences set."
        
        # Build the full prompt using the template
        prompt = CONVERSATION_PROMPT_TEMPLATE.format(
            system_prompt=system_prompt,
            user_preferences=user_preferences,
            conversation_history=conversation_str,
            relevant_memories=memories_str,
            user_message=user_message if user_message else ""
        )
        
        return prompt
    
    def _customize_system_prompt(self):
        """
        Customize the system prompt based on personality settings.
        
        Returns:
            Customized system prompt
        """
        # Start with the base system prompt
        prompt = SYSTEM_PROMPT
        
        # Customize based on personality settings
        prompt += f"\n\nYou should speak in a {self.tone} tone, as a {self.persona}."
        
        # Adjust for emoji usage
        if self.emoji_level == "none":
            prompt += "\nDo not use any emojis in your responses."
        elif self.emoji_level == "minimal":
            prompt += "\nUse emojis very sparingly, only for key points."
        elif self.emoji_level == "moderate":
            prompt += "\nUse emojis moderately to emphasize key points and add warmth."
        elif self.emoji_level == "high":
            prompt += "\nUse emojis frequently to make your responses engaging and lively."
        
        # Adjust for verbosity
        if self.verbosity == "concise":
            prompt += "\nKeep your responses brief and to the point."
        elif self.verbosity == "medium":
            prompt += "\nProvide balanced explanations with enough detail to be helpful."
        elif self.verbosity == "detailed":
            prompt += "\nProvide comprehensive explanations with examples and context."
        
        return prompt
    
    def get_welcome_message(self, user_name="there"):
        """
        Get a welcome message for a user.
        
        Args:
            user_name: User's name or "there" if unknown
            
        Returns:
            Welcome message string
        """
        return WELCOME_MESSAGE_TEMPLATE.format(user_name=user_name)
    
    def get_help_message(self):
        """
        Get the help message.
        
        Returns:
            Help message string
        """
        return HELP_MESSAGE
    
    def format_learning_confirmation(self, session_name):
        """
        Format a confirmation message for learning.
        
        Args:
            session_name: Name of the learning session
            
        Returns:
            Formatted confirmation message
        """
        return (
            f"✅ I've learned and stored this information! You can recall it using:\n"
            f"/recall {session_name}"
        )
    
    def format_recall_header(self, session_name):
        """
        Format a header for recalling information.
        
        Args:
            session_name: Name of the learning session
            
        Returns:
            Formatted recall header
        """
        return f"📚 *{session_name}*\n\n"
