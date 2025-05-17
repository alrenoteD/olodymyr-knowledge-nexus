
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
OpenRouter API Client for Olodymyr

This module handles communication with the OpenRouter API to access various
language models like Claude Haiku and Mistral.
"""

import logging
import json
import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)

class OpenRouterClient:
    """
    Client for communicating with OpenRouter API.
    """
    
    def __init__(self, config):
        """
        Initialize the OpenRouter client.
        
        Args:
            config: Configuration dictionary containing API keys and model preferences
        """
        self.api_key = config["openrouter"]["api_key"]
        if not self.api_key or self.api_key == "YOUR_OPENROUTER_API_KEY":
            logger.error("OpenRouter API key not configured. Please add it to config.json or as an environment variable.")
            raise ValueError("OpenRouter API key not configured")
            
        self.default_model = config["openrouter"]["default_model"]
        self.fallback_model = config["openrouter"]["fallback_model"]
        self.max_tokens = config["openrouter"]["max_tokens"]
        self.base_url = "https://openrouter.ai/api/v1"
        
        # Headers for API requests
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://olodymyr-ai.replit.app",  # Replace with your actual domain
            "X-Title": "Olodymyr AI Assistant"
        }
        
        logger.info(f"Initialized OpenRouter client with default model: {self.default_model}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((requests.exceptions.Timeout, requests.exceptions.ConnectionError))
    )
    async def generate_completion(self, prompt, model=None, temperature=0.7):
        """
        Generate a completion from the OpenRouter API.
        
        Args:
            prompt: The prompt to send to the API
            model: The model to use (defaults to the configured default model)
            temperature: The creativity temperature (0.0 - 1.0)
            
        Returns:
            The generated text
        """
        model = model or self.default_model
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": temperature,
                    "max_tokens": self.max_tokens
                },
                timeout=30
            )
            
            response.raise_for_status()
            response_json = response.json()
            
            # Extract the generated text
            if "choices" in response_json and len(response_json["choices"]) > 0:
                return response_json["choices"][0]["message"]["content"].strip()
            else:
                logger.error(f"Unexpected API response: {response_json}")
                return "I'm sorry, I couldn't generate a response. Please try again."
                
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                logger.warning("Rate limit exceeded, using fallback model")
                return await self.generate_completion(prompt, model=self.fallback_model, temperature=temperature)
            else:
                logger.error(f"HTTP error: {e.response.text if hasattr(e, 'response') else e}")
                raise
                
        except Exception as e:
            logger.error(f"Error generating completion: {str(e)}")
            raise
    
    async def generate_embedding(self, text):
        """
        Generate an embedding vector for the given text.
        
        Args:
            text: The text to embed
            
        Returns:
            The embedding vector
        """
        # Default to OpenAI's embedding model, typically available through OpenRouter
        embedding_model = "openai/text-embedding-ada-002"
        
        try:
            response = requests.post(
                f"{self.base_url}/embeddings",
                headers=self.headers,
                json={
                    "model": embedding_model,
                    "input": text
                },
                timeout=15
            )
            
            response.raise_for_status()
            response_json = response.json()
            
            # Extract the embedding
            if "data" in response_json and len(response_json["data"]) > 0:
                return response_json["data"][0]["embedding"]
            else:
                logger.error(f"Unexpected API response: {response_json}")
                raise ValueError("Failed to get embedding from API")
                
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise

def setup_llm_client(config):
    """
    Set up and initialize the LLM client.
    
    Args:
        config: The configuration dictionary
        
    Returns:
        Configured OpenRouterClient instance
    """
    return OpenRouterClient(config)
