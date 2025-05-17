
# Olodymyr Architecture Documentation

## Overview

Olodymyr is an intelligent AI assistant designed to function with lightweight LLM models while providing rich functionality through carefully designed systems and integrations. This document outlines the architecture, components, dependencies, and design decisions.

## Core Philosophy

The core philosophy behind Olodymyr is to create an AI assistant that:

1. **Maintains intelligence with lightweight models**: Uses context management and memory systems to overcome token limitations
2. **Learns and adapts**: Stores and retrieves information as requested
3. **Teaches effectively**: Explains concepts in a clear, didactic manner
4. **Maintains consistent personality**: Provides a friendly, helpful experience
5. **Works across platforms**: Primarily through Telegram, but extensible

## System Architecture

```
┌──────────────────┐       ┌──────────────────┐       ┌──────────────────┐
│                  │       │                  │       │                  │
│  User Interface  ├───────►  Core Pipeline   ├───────►     Memory       │
│   (Telegram)     │       │                  │       │    Systems       │
│                  │       │                  │       │                  │
└──────────────────┘       └────────┬─────────┘       └──────────────────┘
                                    │                           ▲
                                    ▼                           │
                           ┌──────────────────┐       ┌─────────┴──────────┐
                           │                  │       │                    │
                           │     LLM API      ├───────►     Tools &        │
                           │  (OpenRouter)    │       │   Integrations     │
                           │                  │       │                    │
                           └──────────────────┘       └────────────────────┘
```

## Components and Dependencies

### 1. Core Components

#### Bot Interface (`bot/`)
- **Dependencies**: `python-telegram-bot`
- **Purpose**: Handles communication with users through Telegram
- **Design Rationale**: Telegram provides a ubiquitous, cross-platform interface that requires minimal setup. The python-telegram-bot library offers a robust API with excellent documentation.

#### Core Logic (`core/`)
- **Dependencies**: Internal modules
- **Purpose**: Orchestrates the flow of information, personality, context management
- **Design Rationale**: Modular design allows for easy extension and modification

#### LLM Integration (`llms/`)
- **Dependencies**: `openrouter`, `requests`
- **Purpose**: Communicates with language models
- **Design Rationale**: OpenRouter provides access to multiple models through a unified API, allowing for model switching and fallbacks

#### Memory Systems (`memory/`)
- **Dependencies**: `chromadb`, `supabase-py`
- **Purpose**: Stores and retrieves information
- **Design Rationale**: Dual storage system combines the benefits of vector search (ChromaDB) and relational data (Supabase)

#### Tools (`tools/`)
- **Dependencies**: `beautifulsoup4`, `requests`
- **Purpose**: Provides utility functions like web scraping
- **Design Rationale**: Modular tools can be enabled/disabled based on needs and security considerations

### 2. Key Dependencies

| Dependency | Version | Purpose | Rationale |
|------------|---------|---------|-----------|
| python-telegram-bot | ^20.7 | Telegram API interface | Mature, well-documented library with async support |
| requests | ^2.31.0 | HTTP communication | Standard, reliable HTTP library |
| openai | ^1.3.0 | AI model interface | Required for embeddings and some fallback models |
| chromadb | ^0.4.22 | Vector database | Lightweight, easy to set up vector store for semantic search |
| supabase-py | ^2.3.0 | Database interface | Provides persistent storage with good Python support |
| beautifulsoup4 | ^4.12.2 | Web scraping | Standard library for HTML parsing |
| pydantic | ^2.5.2 | Data validation | Ensures data integrity and schema validation |
| python-dotenv | ^1.0.0 | Environment variables | Secure configuration management |

## Data Flow

1. **Message Reception**
   - User sends message via Telegram
   - Message is preprocessed and user session retrieved

2. **Context Management**
   - Recent conversation context assembled
   - Relevant memories retrieved based on query

3. **LLM Processing**
   - Prompt assembled with context, memories, and personality
   - Sent to appropriate model via OpenRouter
   - Response parsed and post-processed

4. **Memory Management**
   - Important information stored if learning command detected
   - Context updated with new interaction
   - Vector embeddings created for semantic search

5. **Response Delivery**
   - Formatted response sent back to user via Telegram
   - Any actions/tools triggered as needed

## Memory Architecture

Olodymyr uses a multi-tiered memory system:

1. **Short-term Memory**: Recent conversations, stored in-memory
2. **Working Memory**: Current session information, stored in Supabase
3. **Long-term Memory**: Vector store in ChromaDB with references in Supabase
4. **Learning Sessions**: Named collections of information, stored in both systems

## Prompt Engineering

Prompts are carefully designed to:

1. Maintain consistent personality
2. Maximize the value of limited context windows
3. Guide the model toward educational responses
4. Include relevant memories without overwhelming context

## Advanced Features

### 1. Learning System

When a user requests Olodymyr to learn something:

1. Content is processed and chunked appropriately
2. Embeddings are created and stored in ChromaDB
3. Metadata and references stored in Supabase
4. A named session is created for easy retrieval

### 2. Web Scraping

For learning from URLs:

1. Content is fetched and cleaned (removing ads, navigation)
2. Main content is extracted using heuristics
3. Content is summarized if too large
4. Processed through the learning system

### 3. Context Optimization

To maximize the effectiveness of small context windows:

1. Dynamic token budgeting based on conversation
2. Selective memory inclusion based on relevance
3. Compression of historical exchanges
4. Structured formatting to guide model attention

## Security Considerations

1. API keys stored securely using environment variables
2. User access controls for Telegram (optional whitelist)
3. Rate limiting to prevent abuse
4. Sanitization of inputs for web scraping
5. Proper error handling to prevent data leakage

## Extensibility

The modular design allows for easy addition of:

1. New messaging platforms beyond Telegram
2. Additional LLM providers
3. New tools and capabilities
4. Enhanced memory systems

## Performance Optimizations

1. Asynchronous processing where possible
2. Efficient memory retrieval algorithms
3. Caching of frequently used data
4. Compression of historical context

## Limitations and Future Work

1. **Token Limitations**: Even with optimizations, complex reasoning is constrained by model context windows
2. **Retrieval Quality**: Memory retrieval depends on embedding quality
3. **Platform Limitations**: Telegram has message size limits
4. **Model Limitations**: Smaller models may struggle with complex instructions

Future enhancements could include:
1. Multi-modal capabilities (image understanding)
2. More sophisticated memory management
3. Additional platform integrations
4. Self-improvement mechanisms
