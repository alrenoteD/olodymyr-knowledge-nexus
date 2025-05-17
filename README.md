
# Olodymyr AI Assistant

Olodymyr is an intelligent AI assistant designed to function effectively with lightweight LLM models while providing rich functionality through carefully designed systems and integrations.

## Overview

Olodymyr operates as a Telegram bot that can:

- Answer questions and maintain conversation context
- Learn and store knowledge when instructed
- Explain concepts like a professor
- Process and learn from web content
- Access and retrieve stored information

## Features

- **Consistent Personality**: Friendly, educational tone like a helpful professor
- **Memory System**: Stores knowledge in named sessions for later retrieval
- **Web Content Processing**: Can extract and learn from web pages
- **Context Management**: Maintains conversation flow despite token limitations
- **Educational Responses**: Explains concepts clearly with moderate emoji usage

## Setup Instructions

### Prerequisites

- Python 3.8+
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- OpenRouter API Key (for LLM access)
- Supabase Project (optional, for persistent storage)

### Installation

1. Clone the repository:

```bash
git clone https://github.com/username/olodymyr-ai.git
cd olodymyr-ai
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your API keys:

```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key_here
```

4. Run the assistant:

```bash
python main.py
```

## Configuration

Edit `config.json` to customize:

- Default LLM models
- Memory settings
- Personality parameters
- Feature toggles

## Usage

Start a conversation with the bot on Telegram and use these commands:

- `/start` - Initialize the bot
- `/help` - View available commands
- `/learn [name] [content/URL]` - Store information with a name
- `/recall [name]` - Retrieve stored information
- `/clear` - Clear conversation context

## Deployment

### Replit

1. Create a new Replit from the GitHub repository
2. Add your API keys as Replit Secrets
3. Run the bot with `python main.py`
4. Enable "Always On" to keep the bot running

### Railway

1. Connect your GitHub repository to Railway
2. Add environment variables for your API keys
3. Deploy the application

## Architecture

Olodymyr is built with a modular architecture:

- **Bot Interface**: Handles Telegram communication
- **Core Logic**: Manages personality, context, and learning
- **Memory System**: Combines ChromaDB and Supabase for storage
- **LLM Interface**: Communicates with models via OpenRouter
- **Tools**: Provides utilities like web scraping

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
