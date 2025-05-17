
# Olodymyr Integration Guide

This guide explains how to integrate Olodymyr with various services like Telegram, OpenRouter, and Supabase.

## 1. Telegram Bot Integration

### Setup
1. Create a new bot with [@BotFather](https://t.me/BotFather) on Telegram
2. Get your bot token and add it to your config.json:
   ```json
   {
     "telegram": {
       "token": "YOUR_TELEGRAM_BOT_TOKEN",
       "allowed_users": ["user_id_1", "user_id_2"]  // Optional for restrictions
     }
   }
   ```

### How It Works
- The Telegram bot runs as a webhook or polling service (configurable)
- Messages from users are passed to the core processing pipeline
- Responses are formatted with appropriate markdown and sent back
- Sessions are maintained per user ID to keep context
- The bot can handle text, files, links, and images

### Custom Commands
- `/start` - Initialize the bot and receive welcome message
- `/learn <name>` - Start a learning session with specified name
- `/recall <name>` - Recall information from a specific learning session
- `/clear` - Clear current conversation context
- `/help` - Show available commands and usage

## 2. OpenRouter Integration

### Setup
1. Create an account at [OpenRouter](https://openrouter.ai/)
2. Get your API key and add it to your config.json:
   ```json
   {
     "openrouter": {
       "api_key": "YOUR_OPENROUTER_API_KEY",
       "default_model": "claude-haiku",
       "fallback_model": "mistral-small",
       "max_tokens": 4000
     }
   }
   ```

### How It Works
- Olodymyr uses OpenRouter as a unified API to access various LLMs
- Primary models: Claude Haiku and Mistral Small
- Fallback mechanisms are in place if primary model fails
- Context handling optimized for different token windows
- Different prompt templates for different model capabilities

### Model Selection
- The system automatically selects appropriate models based on:
  - Task complexity
  - Context length
  - Required capabilities (code generation, reasoning, etc.)
  - User preferences

## 3. Supabase Integration

### Setup
1. Create a [Supabase](https://supabase.io/) project
2. Set up the following tables:
   - `users`: User information and preferences 
   - `sessions`: Conversation sessions
   - `memories`: Long-term persistent memories
   - `learning_sessions`: Named learning sessions
3. Add your credentials to config.json:
   ```json
   {
     "supabase": {
       "url": "YOUR_SUPABASE_URL",
       "anon_key": "YOUR_SUPABASE_ANON_KEY",
       "service_role_key": "YOUR_SUPABASE_SERVICE_ROLE_KEY"
     }
   }
   ```

### How It Works
- User data is stored in Supabase for persistence
- Memory vectors are stored in ChromaDB (local) with references in Supabase
- Session history is maintained in both temporary memory and long-term storage
- Learning sessions are stored with metadata for easy retrieval
- Analytics data is collected for improving bot responses

### Database Schema
```sql
CREATE TABLE users (
  id TEXT PRIMARY KEY,
  settings JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sessions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id TEXT REFERENCES users(id),
  name TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE messages (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  session_id UUID REFERENCES sessions(id),
  role TEXT CHECK (role IN ('user', 'assistant')),
  content TEXT,
  timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE learning_sessions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id TEXT REFERENCES users(id),
  name TEXT,
  description TEXT,
  content TEXT,
  source TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

## 4. ChromaDB Integration

### Setup
1. Install ChromaDB locally: `pip install chromadb`
2. Configure storage location in config.json:
   ```json
   {
     "chromadb": {
       "persist_directory": "./chroma_db"
     }
   }
   ```

### How It Works
- ChromaDB stores vector embeddings for efficient semantic search
- Each memory chunk is embedded and stored with metadata
- Retrieval is performed based on semantic similarity
- Integration with Supabase ensures references are maintained between systems

## 5. Web Scraping / Content Processing

### Setup
- Uses BeautifulSoup and Requests libraries
- No additional setup required beyond installing dependencies

### How It Works
- When a URL is provided with a learning command, the scraper:
  1. Fetches the content
  2. Extracts meaningful text (removing ads, navigation, etc.)
  3. Chunks content appropriately
  4. Processes and stores in appropriate memory systems
  5. Creates embeddings for semantic search

## Deployment Instructions

### Railway Deployment
1. Connect your GitHub repository to Railway
2. Add environment variables for all API keys and tokens
3. Configure the service to run `python main.py`
4. Set up appropriate resources (memory, CPU)

### Replit Deployment
1. Create a new Replit from your GitHub repo
2. Add secrets in Replit for all API keys and tokens
3. Configure `.replit` file to run `python main.py`
4. Use Replit's "Always On" feature to keep the bot running

## Monitoring and Maintenance

- Logs are stored in the `logs` directory
- Use the admin commands to check system status
- Regular database backups are recommended
- Monitor token usage via OpenRouter dashboard
