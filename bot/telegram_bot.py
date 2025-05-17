
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Telegram Bot for Olodymyr AI Assistant

This module handles the Telegram bot interface for the Olodymyr AI assistant,
including message handling, command processing, and user interactions.
"""

import logging
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logger = logging.getLogger(__name__)

async def setup_telegram_bot(config, context_manager, learning_engine, personality_engine, llm_client):
    """
    Set up and configure the Telegram bot.
    
    Args:
        config: The configuration dictionary
        context_manager: The context management system
        learning_engine: The learning and memory system
        personality_engine: The personality engine
        llm_client: The LLM client for generating responses
    
    Returns:
        The configured Application instance
    """
    # Get bot token from config
    token = config["telegram"]["token"]
    if not token or token == "YOUR_TELEGRAM_BOT_TOKEN":
        logger.error("Telegram bot token not configured. Please add it to config.json or as an environment variable.")
        raise ValueError("Telegram bot token not configured")
    
    # Create application
    application = Application.builder().token(token).build()
    
    # Get bot info
    bot_info = await application.bot.get_me()
    logger.info(f"Bot initialized: @{bot_info.username}")
    
    # Create handlers
    from bot.handlers import (
        start_command,
        help_command,
        learn_command,
        recall_command,
        clear_command,
        handle_message,
        handle_error
    )
    
    # Initialize handler functions with dependencies
    handler_dependencies = {
        "config": config,
        "context_manager": context_manager,
        "learning_engine": learning_engine,
        "personality_engine": personality_engine,
        "llm_client": llm_client
    }
    
    # Register command handlers
    application.add_handler(CommandHandler("start", 
                                           lambda update, context: start_command(update, context, **handler_dependencies)))
    application.add_handler(CommandHandler("help", 
                                           lambda update, context: help_command(update, context, **handler_dependencies)))
    application.add_handler(CommandHandler("learn", 
                                           lambda update, context: learn_command(update, context, **handler_dependencies)))
    application.add_handler(CommandHandler("recall", 
                                           lambda update, context: recall_command(update, context, **handler_dependencies)))
    application.add_handler(CommandHandler("clear", 
                                           lambda update, context: clear_command(update, context, **handler_dependencies)))
    
    # Register message handler
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, 
        lambda update, context: handle_message(update, context, **handler_dependencies)
    ))
    
    # Register error handler
    application.add_error_handler(lambda update, context: handle_error(update, context, config))
    
    # Start the bot
    if config["telegram"].get("use_webhook", False) and config["telegram"].get("webhook_url"):
        # Webhook mode (for production)
        webhook_url = config["telegram"]["webhook_url"]
        await application.bot.set_webhook(webhook_url)
        logger.info(f"Bot started in webhook mode: {webhook_url}")
    else:
        # Polling mode (for development)
        await application.initialize()
        await application.start()
        logger.info("Bot started in polling mode")
        
    return application
