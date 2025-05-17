
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Telegram Bot Command and Message Handlers for Olodymyr

This module contains the handler functions for various commands and messages
received by the Telegram bot.
"""

import logging
import asyncio
import traceback
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

# Command handlers

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE, **kwargs):
    """
    Handle /start command - introduce the bot and its capabilities.
    
    Args:
        update: The update containing the command
        context: The context of the command
        **kwargs: Additional dependencies (config, context_manager, etc.)
    """
    config = kwargs.get("config")
    personality_engine = kwargs.get("personality_engine")
    
    user = update.effective_user
    logger.info(f"User {user.id} started the bot")
    
    # Check if user is allowed (if whitelist is enabled)
    allowed_users = config["telegram"].get("allowed_users", [])
    if allowed_users and str(user.id) not in allowed_users:
        logger.warning(f"Unauthorized access attempt by user {user.id}")
        await update.message.reply_text(
            "Sorry, you are not authorized to use this bot."
        )
        return
    
    # Get welcome message from personality engine
    welcome_message = personality_engine.get_welcome_message(user.first_name)
    
    await update.message.reply_text(
        welcome_message,
        parse_mode=ParseMode.MARKDOWN
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE, **kwargs):
    """
    Handle /help command - provide information about available commands.
    
    Args:
        update: The update containing the command
        context: The context of the command
        **kwargs: Additional dependencies
    """
    personality_engine = kwargs.get("personality_engine")
    help_message = personality_engine.get_help_message()
    
    await update.message.reply_text(
        help_message,
        parse_mode=ParseMode.MARKDOWN
    )

async def learn_command(update: Update, context: ContextTypes.DEFAULT_TYPE, **kwargs):
    """
    Handle /learn command - create a new learning session.
    
    Format: /learn [session_name] [content or URL]
    
    Args:
        update: The update containing the command
        context: The context of the command
        **kwargs: Additional dependencies
    """
    learning_engine = kwargs.get("learning_engine")
    config = kwargs.get("config")
    
    # Parse arguments
    args = context.args
    if len(args) < 2:
        await update.message.reply_text(
            "Usage: /learn [session_name] [content or URL]\n\n"
            "Example:\n"
            "/learn python_basics Python is a programming language that..."
        )
        return
    
    session_name = args[0]
    content = " ".join(args[1:])
    user_id = str(update.effective_user.id)
    
    # Check if content is a URL and scraping is enabled
    if content.startswith("http") and config["features"].get("web_scraping", True):
        # Show processing message
        processing_message = await update.message.reply_text("🔍 Processing web content. This may take a moment...")
        
        try:
            # Import web scraper here to avoid circular imports
            from tools.web_scraper import scrape_webpage
            
            # Scrape the webpage
            scraped_content = await scrape_webpage(content)
            
            # Store the scraped content
            session_id = await learning_engine.create_learning_session(
                user_id=user_id,
                name=session_name,
                content=scraped_content,
                description=f"Content scraped from {content}",
                source=content
            )
            
            await processing_message.edit_text(
                f"✅ Successfully learned content from {content}\n\n"
                f"Stored as: *{session_name}*\n\n"
                f"You can recall this information using:\n"
                f"`/recall {session_name}`",
                parse_mode=ParseMode.MARKDOWN
            )
            
        except Exception as e:
            logger.error(f"Error scraping webpage: {e}")
            await processing_message.edit_text(
                f"❌ Failed to process the URL: {content}\n\n"
                f"Error: {str(e)}"
            )
    else:
        # Store the provided content directly
        try:
            session_id = await learning_engine.create_learning_session(
                user_id=user_id,
                name=session_name,
                content=content,
                description=f"User-provided content"
            )
            
            await update.message.reply_text(
                f"✅ Successfully stored information as: *{session_name}*\n\n"
                f"You can recall this information using:\n"
                f"`/recall {session_name}`",
                parse_mode=ParseMode.MARKDOWN
            )
            
        except Exception as e:
            logger.error(f"Error creating learning session: {e}")
            await update.message.reply_text(
                f"❌ Failed to store information: {str(e)}"
            )

async def recall_command(update: Update, context: ContextTypes.DEFAULT_TYPE, **kwargs):
    """
    Handle /recall command - retrieve information from a learning session.
    
    Format: /recall [session_name]
    
    Args:
        update: The update containing the command
        context: The context of the command
        **kwargs: Additional dependencies
    """
    learning_engine = kwargs.get("learning_engine")
    llm_client = kwargs.get("llm_client")
    
    # Parse arguments
    args = context.args
    if not args:
        await update.message.reply_text(
            "Usage: /recall [session_name]\n\n"
            "Example:\n"
            "/recall python_basics"
        )
        return
    
    session_name = args[0]
    user_id = str(update.effective_user.id)
    
    # Show typing indication
    await update.message.chat.send_action("typing")
    
    try:
        # Retrieve learning session
        session = await learning_engine.get_learning_session(user_id, session_name)
        
        if not session:
            await update.message.reply_text(
                f"❌ No learning session found with name: *{session_name}*",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Generate a teaching response based on the session content
        teaching_prompt = f"""
        You are Olodymyr, an educational AI assistant. 
        You need to explain the following information in a clear, educational way, 
        as if you're a friendly professor teaching a student. 
        Use examples where appropriate and organize your explanation well.
        
        Here is the information to explain:
        
        {session['content']}
        
        Remember to keep a friendly tone, use moderate emojis where appropriate, 
        and make the explanation engaging and easy to understand.
        """
        
        # Generate response
        response = await llm_client.generate_completion(teaching_prompt)
        
        # Format and send the response
        await update.message.reply_text(
            f"📚 *{session_name}*\n\n{response}",
            parse_mode=ParseMode.MARKDOWN
        )
        
    except Exception as e:
        logger.error(f"Error recalling learning session: {e}")
        await update.message.reply_text(
            f"❌ Error retrieving information: {str(e)}"
        )

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE, **kwargs):
    """
    Handle /clear command - clear the current conversation context.
    
    Args:
        update: The update containing the command
        context: The context of the command
        **kwargs: Additional dependencies
    """
    context_manager = kwargs.get("context_manager")
    user_id = str(update.effective_user.id)
    
    await context_manager.clear_context(user_id)
    await update.message.reply_text(
        "🧹 Conversation context cleared. Starting fresh!"
    )

# Message handler

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE, **kwargs):
    """
    Handle regular messages - process the message and generate a response.
    
    Args:
        update: The update containing the message
        context: The context of the message
        **kwargs: Additional dependencies
    """
    config = kwargs.get("config")
    context_manager = kwargs.get("context_manager")
    learning_engine = kwargs.get("learning_engine")
    personality_engine = kwargs.get("personality_engine")
    llm_client = kwargs.get("llm_client")
    
    user_id = str(update.effective_user.id)
    message_text = update.message.text
    
    # Show typing indication
    await update.message.chat.send_action("typing")
    
    try:
        # Add user message to context
        await context_manager.add_message(user_id, "user", message_text)
        
        # Check for learning request
        if message_text.lower().startswith(("learn", "aprenda isso", "guarde isso")):
            # Extract learning content
            content = message_text.split(" ", 1)[1] if " " in message_text else ""
            if not content:
                await update.message.reply_text(
                    "Please provide content to learn after 'learn'/'aprenda isso'/'guarde isso'."
                )
                return
                
            # Generate a name for this learning session
            session_name = f"session_{user_id}_{context.user_data.get('session_count', 0)}"
            context.user_data['session_count'] = context.user_data.get('session_count', 0) + 1
            
            # Store the content
            await learning_engine.create_learning_session(
                user_id=user_id,
                name=session_name,
                content=content,
                description="Content learned from chat"
            )
            
            response = f"✅ I've learned and stored this information! You can recall it using:\n/recall {session_name}"
            
        else:
            # Get conversation context
            conversation_history = await context_manager.get_context(user_id)
            
            # Get relevant memories (if any)
            relevant_memories = await learning_engine.get_relevant_memories(user_id, message_text)
            
            # Build the prompt with personality, context and relevant memories
            prompt = personality_engine.build_prompt(
                conversation_history=conversation_history,
                relevant_memories=relevant_memories
            )
            
            # Generate response from LLM
            response = await llm_client.generate_completion(prompt)
        
        # Add assistant response to context
        await context_manager.add_message(user_id, "assistant", response)
        
        # Send the response (in chunks if needed due to Telegram's message size limit)
        if len(response) > 4000:
            chunks = [response[i:i+4000] for i in range(0, len(response), 4000)]
            for chunk in chunks:
                await update.message.reply_text(chunk, parse_mode=ParseMode.MARKDOWN)
        else:
            await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
            
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        logger.error(traceback.format_exc())
        await update.message.reply_text(
            "Sorry, I encountered an error while processing your message. Please try again."
        )

# Error handler

async def handle_error(update: Update, context: ContextTypes.DEFAULT_TYPE, config):
    """
    Handle errors that occur during message processing.
    
    Args:
        update: The update that caused the error
        context: The context in which the error occurred
        config: The bot configuration
    """
    logger.error(f"Exception while handling an update: {context.error}")
    logger.error(traceback.format_exc())
    
    # Send error message to user if update is available
    if update is not None and update.effective_message is not None:
        await update.effective_message.reply_text(
            "Sorry, something went wrong while processing your request."
        )
    
    # Send error details to admin if configured
    admin_chat_id = config.get("admin_chat_id")
    if admin_chat_id:
        error_text = f"Error processing update:\n{traceback.format_exc()}"
        try:
            await context.bot.send_message(admin_chat_id, error_text)
        except Exception as e:
            logger.error(f"Failed to send error message to admin: {e}")
