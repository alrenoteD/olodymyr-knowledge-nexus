
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ChromaDB Memory System for Olodymyr AI Assistant

This module implements vector storage using ChromaDB for semantic memory.
"""

import os
import logging
import asyncio
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings

logger = logging.getLogger(__name__)

class ChromaMemory:
    """
    ChromaDB-based vector memory storage.
    """
    
    def __init__(self, config):
        """
        Initialize ChromaDB memory.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.persist_directory = config["chromadb"].get("persist_directory", "./chroma_db")
        self.collection_name = config["chromadb"].get("collection_name", "olodymyr_memories")
        self.embedding_function = None
        self.client = None
        self.collection = None
        
        logger.info(f"ChromaMemory initialized with persist_directory: {self.persist_directory}")
    
    async def initialize(self):
        """
        Initialize ChromaDB client and collection.
        
        Returns:
            True if successful
        """
        try:
            # Ensure persist directory exists
            os.makedirs(self.persist_directory, exist_ok=True)
            
            # Create client
            self.client = chromadb.Client(Settings(
                persist_directory=self.persist_directory,
                chroma_db_impl="duckdb+parquet",
            ))
            
            # Set up embedding function based on config
            embedding_type = self.config["chromadb"].get("embedding_function", "openai")
            
            if embedding_type == "openai":
                try:
                    from chromadb.utils import embedding_functions
                    
                    # If OpenAI API key is provided, use OpenAI embeddings
                    openai_api_key = os.environ.get("OPENAI_API_KEY")
                    if openai_api_key:
                        self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
                            api_key=openai_api_key,
                            model_name="text-embedding-ada-002"
                        )
                        logger.info("Using OpenAI embedding function")
                    else:
                        # Fall back to default embedding function
                        self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
                        logger.info("Using default embedding function (OpenAI API key not found)")
                        
                except ImportError:
                    logger.warning("ChromaDB OpenAI embedding functions not available, using default")
                    self.embedding_function = None
            else:
                self.embedding_function = None
                logger.info("Using default embedding function")
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function,
                metadata={"description": "Olodymyr's memories"}
            )
            
            logger.info(f"ChromaDB collection '{self.collection_name}' initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise
    
    async def add_vector(self, id: str, text: str, metadata: Dict = None) -> bool:
        """
        Add a vector to the collection.
        
        Args:
            id: Unique identifier
            text: Text content
            metadata: Optional metadata
            
        Returns:
            True if successful
        """
        try:
            self.collection.add(
                ids=[id],
                documents=[text],
                metadatas=[metadata or {}]
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to add vector: {e}")
            return False
    
    async def search(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Search for relevant vectors.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of relevant documents with metadata
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=limit
            )
            
            # Format results
            formatted_results = []
            
            if results and "documents" in results and results["documents"]:
                documents = results["documents"][0]  # First query result
                metadatas = results["metadatas"][0] if "metadatas" in results else [{}] * len(documents)
                distances = results["distances"][0] if "distances" in results else [1.0] * len(documents)
                
                for i, doc in enumerate(documents):
                    formatted_results.append({
                        "text": doc,
                        "metadata": metadatas[i] if i < len(metadatas) else {},
                        "distance": distances[i] if i < len(distances) else 1.0
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to search vectors: {e}")
            return []
    
    async def delete_vectors(self, session_id: str) -> bool:
        """
        Delete vectors associated with a session.
        
        Args:
            session_id: Session ID
            
        Returns:
            True if successful
        """
        try:
            # Get all IDs with this session_id in metadata
            results = self.collection.get(
                where={"session_id": session_id}
            )
            
            if results and "ids" in results and results["ids"]:
                # Delete the vectors
                self.collection.delete(
                    ids=results["ids"]
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete vectors for session {session_id}: {e}")
            return False
    
    async def count_vectors(self) -> int:
        """
        Count total vectors in the collection.
        
        Returns:
            Number of vectors
        """
        try:
            return self.collection.count()
            
        except Exception as e:
            logger.error(f"Failed to count vectors: {e}")
            return 0
