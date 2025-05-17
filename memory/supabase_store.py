
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Supabase Storage for Olodymyr AI Assistant

This module implements relational data storage using Supabase.
"""

import logging
from typing import Dict, List, Optional, Any
import json
from datetime import datetime
import uuid
import asyncio

logger = logging.getLogger(__name__)

class SupabaseStore:
    """
    Supabase-based relational data storage.
    """
    
    def __init__(self, config):
        """
        Initialize Supabase storage.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.url = config["supabase"]["url"]
        self.anon_key = config["supabase"]["anon_key"]
        self.service_role_key = config["supabase"].get("service_role_key")
        self.client = None
        
        logger.info("SupabaseStore initialized")
    
    async def initialize(self):
        """
        Initialize Supabase client and verify connection.
        
        Returns:
            True if successful
        """
        try:
            # Import supabase client
            from supabase import create_client
            
            # Check if keys are configured
            if not self.url or not self.anon_key or self.url == "YOUR_SUPABASE_URL" or self.anon_key == "YOUR_SUPABASE_ANON_KEY":
                logger.warning("Supabase not fully configured. Using mock storage.")
                self.client = None
                self._setup_mock_storage()
                return True
            
            # Initialize client
            self.client = create_client(self.url, self.anon_key)
            
            # Test connection
            test = self.client.table("test").select("*").limit(1).execute()
            logger.info("Supabase connection successful")
            
            return True
            
        except ImportError:
            logger.warning("Supabase library not installed. Using mock storage.")
            self.client = None
            self._setup_mock_storage()
            return True
            
        except Exception as e:
            logger.warning(f"Supabase initialization failed: {e}. Using mock storage.")
            self.client = None
            self._setup_mock_storage()
            return True
    
    def _setup_mock_storage(self):
        """Set up mock storage using dictionaries."""
        self.mock_users = {}
        self.mock_sessions = {}
        self.mock_messages = []
        self.mock_learning_sessions = {}
        logger.info("Mock storage initialized")
    
    # User management
    
    async def get_user(self, user_id: str) -> Dict:
        """
        Get user data.
        
        Args:
            user_id: User ID
            
        Returns:
            User data dictionary
        """
        try:
            if self.client:
                response = self.client.table("users").select("*").eq("id", user_id).execute()
                
                if response.data and len(response.data) > 0:
                    return response.data[0]
                else:
                    # Create user if not exists
                    new_user = {
                        "id": user_id,
                        "settings": json.dumps({"created_at": datetime.now().isoformat()})
                    }
                    self.client.table("users").insert(new_user).execute()
                    return new_user
            else:
                # Mock implementation
                if user_id not in self.mock_users:
                    self.mock_users[user_id] = {
                        "id": user_id,
                        "settings": {"created_at": datetime.now().isoformat()},
                        "created_at": datetime.now().isoformat()
                    }
                return self.mock_users[user_id]
                
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            
            # Return default user data
            return {
                "id": user_id,
                "settings": {},
                "created_at": datetime.now().isoformat()
            }
    
    async def get_user_preferences(self, user_id: str) -> Dict:
        """
        Get user preferences.
        
        Args:
            user_id: User ID
            
        Returns:
            User preferences dictionary
        """
        user = await self.get_user(user_id)
        
        if self.client:
            return json.loads(user.get("settings", "{}"))
        else:
            return user.get("settings", {})
    
    async def update_user_preferences(self, user_id: str, preferences: Dict) -> bool:
        """
        Update user preferences.
        
        Args:
            user_id: User ID
            preferences: Preferences dictionary
            
        Returns:
            True if successful
        """
        try:
            user = await self.get_user(user_id)
            
            if self.client:
                current_settings = json.loads(user.get("settings", "{}"))
                updated_settings = {**current_settings, **preferences}
                
                self.client.table("users").update({
                    "settings": json.dumps(updated_settings)
                }).eq("id", user_id).execute()
            else:
                # Mock implementation
                if user_id not in self.mock_users:
                    await self.get_user(user_id)
                    
                current_settings = self.mock_users[user_id].get("settings", {})
                self.mock_users[user_id]["settings"] = {**current_settings, **preferences}
                
            return True
            
        except Exception as e:
            logger.error(f"Error updating user preferences: {e}")
            return False
    
    # Conversation history
    
    async def get_conversation_history(self, user_id: str, limit: int = 10) -> List[Dict]:
        """
        Get conversation history for a user.
        
        Args:
            user_id: User ID
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of message dictionaries
        """
        try:
            if self.client:
                # Get latest session for user
                session_response = self.client.table("sessions").select("id").eq("user_id", user_id).order("created_at", desc=True).limit(1).execute()
                
                if not session_response.data:
                    # Create new session
                    session_id = str(uuid.uuid4())
                    self.client.table("sessions").insert({
                        "id": session_id,
                        "user_id": user_id,
                        "name": "New conversation",
                        "created_at": datetime.now().isoformat(),
                        "updated_at": datetime.now().isoformat()
                    }).execute()
                else:
                    session_id = session_response.data[0]["id"]
                
                # Get messages for session
                messages_response = self.client.table("messages").select("*").eq("session_id", session_id).order("timestamp", desc=True).limit(limit).execute()
                
                # Reverse to get chronological order
                return list(reversed(messages_response.data))
            else:
                # Mock implementation
                user_messages = [msg for msg in self.mock_messages if msg.get("user_id") == user_id]
                return sorted(user_messages[-limit:], key=lambda x: x.get("timestamp", ""))
                
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return []
    
    async def add_message_to_history(self, user_id: str, role: str, content: str) -> bool:
        """
        Add a message to conversation history.
        
        Args:
            user_id: User ID
            role: Message role ('user' or 'assistant')
            content: Message content
            
        Returns:
            True if successful
        """
        try:
            timestamp = datetime.now().isoformat()
            
            if self.client:
                # Get latest session for user
                session_response = self.client.table("sessions").select("id").eq("user_id", user_id).order("created_at", desc=True).limit(1).execute()
                
                if not session_response.data:
                    # Create new session
                    session_id = str(uuid.uuid4())
                    self.client.table("sessions").insert({
                        "id": session_id,
                        "user_id": user_id,
                        "name": "New conversation",
                        "created_at": timestamp,
                        "updated_at": timestamp
                    }).execute()
                else:
                    session_id = session_response.data[0]["id"]
                    # Update session timestamp
                    self.client.table("sessions").update({
                        "updated_at": timestamp
                    }).eq("id", session_id).execute()
                
                # Add message
                message_id = str(uuid.uuid4())
                self.client.table("messages").insert({
                    "id": message_id,
                    "session_id": session_id,
                    "role": role,
                    "content": content,
                    "timestamp": timestamp
                }).execute()
            else:
                # Mock implementation
                message_id = str(uuid.uuid4())
                self.mock_messages.append({
                    "id": message_id,
                    "user_id": user_id,
                    "role": role,
                    "content": content,
                    "timestamp": timestamp
                })
                
            return True
            
        except Exception as e:
            logger.error(f"Error adding message to history: {e}")
            return False
    
    async def clear_conversation_history(self, user_id: str) -> bool:
        """
        Clear conversation history for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            True if successful
        """
        try:
            if self.client:
                # Get latest session for user
                session_response = self.client.table("sessions").select("id").eq("user_id", user_id).order("created_at", desc=True).limit(1).execute()
                
                if session_response.data:
                    session_id = session_response.data[0]["id"]
                    
                    # Delete messages for session
                    self.client.table("messages").delete().eq("session_id", session_id).execute()
                    
                    # Update session timestamp
                    self.client.table("sessions").update({
                        "updated_at": datetime.now().isoformat()
                    }).eq("id", session_id).execute()
            else:
                # Mock implementation
                self.mock_messages = [msg for msg in self.mock_messages if msg.get("user_id") != user_id]
                
            return True
            
        except Exception as e:
            logger.error(f"Error clearing conversation history: {e}")
            return False
    
    # Learning sessions
    
    async def create_learning_session(self, user_id: str, name: str, content: str, 
                                    description: str = None, source: str = None) -> str:
        """
        Create a new learning session.
        
        Args:
            user_id: User ID
            name: Session name
            content: Session content
            description: Optional description
            source: Optional source (like URL)
            
        Returns:
            Session ID if successful
        """
        try:
            session_id = str(uuid.uuid4())
            timestamp = datetime.now().isoformat()
            
            session_data = {
                "id": session_id,
                "user_id": user_id,
                "name": name,
                "description": description or "",
                "content": content,
                "source": source,
                "created_at": timestamp,
                "updated_at": timestamp
            }
            
            if self.client:
                self.client.table("learning_sessions").insert(session_data).execute()
            else:
                # Mock implementation
                self.mock_learning_sessions[session_id] = session_data
                
            return session_id
            
        except Exception as e:
            logger.error(f"Error creating learning session: {e}")
            raise
    
    async def get_learning_session(self, session_id: str) -> Dict:
        """
        Get a learning session by ID.
        
        Args:
            session_id: Session ID
            
        Returns:
            Session dictionary or None if not found
        """
        try:
            if self.client:
                response = self.client.table("learning_sessions").select("*").eq("id", session_id).execute()
                
                if response.data and len(response.data) > 0:
                    return response.data[0]
                else:
                    return None
            else:
                # Mock implementation
                return self.mock_learning_sessions.get(session_id)
                
        except Exception as e:
            logger.error(f"Error getting learning session: {e}")
            return None
    
    async def get_learning_session_by_name(self, user_id: str, name: str) -> Dict:
        """
        Get a learning session by name.
        
        Args:
            user_id: User ID
            name: Session name
            
        Returns:
            Session dictionary or None if not found
        """
        try:
            if self.client:
                response = self.client.table("learning_sessions").select("*").eq("user_id", user_id).eq("name", name).execute()
                
                if response.data and len(response.data) > 0:
                    return response.data[0]
                else:
                    return None
            else:
                # Mock implementation
                for session in self.mock_learning_sessions.values():
                    if session.get("user_id") == user_id and session.get("name") == name:
                        return session
                return None
                
        except Exception as e:
            logger.error(f"Error getting learning session by name: {e}")
            return None
    
    async def list_learning_sessions(self, user_id: str) -> List[Dict]:
        """
        List all learning sessions for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of session dictionaries
        """
        try:
            if self.client:
                response = self.client.table("learning_sessions").select("id,name,description,created_at").eq("user_id", user_id).order("created_at", desc=True).execute()
                return response.data
            else:
                # Mock implementation
                return [
                    {
                        "id": session_id,
                        "name": session.get("name"),
                        "description": session.get("description"),
                        "created_at": session.get("created_at")
                    }
                    for session_id, session in self.mock_learning_sessions.items()
                    if session.get("user_id") == user_id
                ]
                
        except Exception as e:
            logger.error(f"Error listing learning sessions: {e}")
            return []
    
    async def delete_learning_session(self, session_id: str) -> bool:
        """
        Delete a learning session.
        
        Args:
            session_id: Session ID
            
        Returns:
            True if successful
        """
        try:
            if self.client:
                self.client.table("learning_sessions").delete().eq("id", session_id).execute()
            else:
                # Mock implementation
                if session_id in self.mock_learning_sessions:
                    del self.mock_learning_sessions[session_id]
                    
            return True
            
        except Exception as e:
            logger.error(f"Error deleting learning session: {e}")
            return False
    
    async def update_learning_session(self, session_id: str, updates: Dict) -> bool:
        """
        Update a learning session.
        
        Args:
            session_id: Session ID
            updates: Dictionary of fields to update
            
        Returns:
            True if successful
        """
        try:
            updates["updated_at"] = datetime.now().isoformat()
            
            if self.client:
                self.client.table("learning_sessions").update(updates).eq("id", session_id).execute()
            else:
                # Mock implementation
                if session_id in self.mock_learning_sessions:
                    self.mock_learning_sessions[session_id].update(updates)
                    
            return True
            
        except Exception as e:
            logger.error(f"Error updating learning session: {e}")
            return False
