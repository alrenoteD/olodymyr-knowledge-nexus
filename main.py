
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Olodymyr AI Assistant - Main Entry Point

This script initializes and runs the Olodymyr AI assistant,
configuring all necessary components and starting the Telegram bot.
"""

import os
import json
import logging
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler("logs/olodymyr.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Ensure necessary directories exist
os.makedirs("logs", exist_ok=True)
os.makedirs("data", exist_ok=True)
os.makedirs("chroma_db", exist_ok=True)

def load_config():
    """Load configuration from config.json file and environment variables."""
    try:
        with open("config.json", "r") as config_file:
            config = json.load(config_file)
        
        # Override config with environment variables if available
        if os.getenv("TELEGRAM_BOT_TOKEN"):
            config["telegram"]["token"] = os.getenv("TELEGRAM_BOT_TOKEN")
        
        if os.getenv("OPENROUTER_API_KEY"):
            config["openrouter"]["api_key"] = os.getenv("OPENROUTER_API_KEY")
        
        if os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_KEY"):
            config["supabase"]["url"] = os.getenv("SUPABASE_URL")
            config["supabase"]["anon_key"] = os.getenv("SUPABASE_KEY")
            if os.getenv("SUPABASE_SERVICE_ROLE_KEY"):
                config["supabase"]["service_role_key"] = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        return config
    
    except FileNotFoundError:
        logger.error("Config file not found. Please create a config.json file.")
        raise
    
    except json.JSONDecodeError:
        logger.error("Config file is not valid JSON. Please check the format.")
        raise

async def main():
    """Initialize and run the Olodymyr AI assistant."""
    # Load configuration
    config = load_config()
    logger.info(f"Starting {config['bot_name']} v{config['version']}")
    
    try:
        # Import components (done here to handle import errors gracefully)
        from bot.telegram_bot import setup_telegram_bot
        from memory.memory_api import setup_memory_systems
        from llms.openrouter_client import setup_llm_client
        from core.context_manager import ContextManager
        from core.learning_engine import LearningEngine
        from core.personality import PersonalityEngine
        
        # Initialize memory systems
        logger.info("Setting up memory systems...")
        memory_system = await setup_memory_systems(config)
        
        # Initialize LLM client
        logger.info("Setting up LLM client...")
        llm_client = setup_llm_client(config)
        
        # Initialize core components
        logger.info("Setting up core components...")
        context_manager = ContextManager(config, memory_system)
        learning_engine = LearningEngine(config, memory_system, llm_client)
        personality_engine = PersonalityEngine(config)
        
        # Initialize and start Telegram bot
        logger.info("Starting Telegram bot...")
        bot = await setup_telegram_bot(
            config,
            context_manager,
            learning_engine,
            personality_engine,
            llm_client
        )
        
        logger.info(f"{config['bot_name']} is now running!")
        
        # Keep the bot running until interrupted
        await bot.idle()
        
    except ImportError as e:
        logger.error(f"Failed to import required modules: {e}")
        logger.error("Please check that all dependencies are installed.")
    except Exception as e:
        logger.error(f"An error occurred during initialization: {e}")
        raise

if __name__ == "__main__":
    try:
        # Create event loop and run main function
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user.")
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
