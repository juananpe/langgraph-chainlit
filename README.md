# LangGraph with Chainlit and SQLite Memory

LangGraph is a conversational AI framework designed to facilitate the creation of complex conversational workflows. It leverages the power of LangChain, a modular AI framework, to enable the integration of various AI tools and models into a single, cohesive system.

## Key Features

* Modular architecture allowing for easy integration of new AI tools and models
* Support for conditional workflows based on user input and AI model outputs
* Real-time conversation handling with streaming capabilities
* Integration with Tavily for web search and document retrieval
* Support for multiple AI models, including OpenAI and Tavily
* **Persistent memory using SQLite**: Conversations are saved and can be resumed across sessions

## Memory Implementation

This application now includes persistent memory using SQLite checkpointing with user authentication. This means:

- **Conversation History**: All messages are saved to a local SQLite database (`checkpoints.db`)
- **User Authentication**: Each user has their own private conversation history
- **Thread-based Memory**: Each authenticated user has their own conversation thread
- **Cross-session Persistence**: Conversations are preserved even if the application restarts
- **Automatic State Management**: LangGraph automatically manages the conversation state per user

### How Memory Works

1. Users must log in with their credentials (username/password)
2. Each user's conversation is identified by a unique `thread_id` based on their username
3. When a user sends a message, it's stored in the SQLite database linked to their thread
4. The graph automatically loads the user's previous messages when they log in again
5. The AI model has access to the full conversation history for context
6. Each user's conversation is completely private and separate from other users

### Default Users

For testing, the following users are available:

- **admin** / admin123 (Administrator)
- **maria** / guapo123 (Mikel Garcia)
- **juan** / fe123 (Juan Pérez)

> **Note**: In production, you should use a proper database for user management and hash passwords securely.

## Getting Started

To get started with LangGraph, follow these steps:

### 1. Set up the virtual environment (using uv)

```bash
# Create a virtual environment
uv venv

# Activate the virtual environment
source .venv/bin/activate  # On Linux/Mac
# or
.venv\Scripts\activate  # On Windows
```

### 2. Install dependencies

```bash
# Using uv (recommended)
uv pip install -r requirements.txt

# Or using regular pip
pip install -r requirements.txt
```

### 3. Set up environment variables

Create a `.env` file in the project root by copying `.env.sample`:

```bash
cp .env.sample .env
```

Then edit the `.env` file and add your API keys:

```bash
OPENAI_API_KEY="sk-proj-..."
TAVILY_API_KEY="tvly-..."
CHAINLIT_AUTH_SECRET="..."  # Generate with: chainlit create-secret
LANGSMITH_API_KEY="lsv2_pt_..."  # Optional
LANGSMITH_TRACING=false
LANGSMITH_ENDPOINT="https://api.smith.langchain.com"
LANGSMITH_PROJECT="langgraph-tavily"
```

To generate the authentication secret, run:

```bash
uv run chainlit create-secret
```

Copy the output and add it to your `.env` file as `CHAINLIT_AUTH_SECRET`.

### 4. Run the application

```bash
uv run chainlit run app.py
```

### 5. Interact with the chatbot

- Open your browser to `http://localhost:8000`
- **Log in** with one of the test user accounts (see Default Users section)
- Start chatting with the AI assistant
- Ask questions that require web search (e.g., "What's the weather in San Francisco?")
- The AI will remember your conversation history automatically
- Each user has their own private conversation history
- Try logging in with different users to see separate conversations

## Configuration

LangGraph relies on environment variables for configuration. The following variables are required:

* `OPENAI_API_KEY`: Your OpenAI API key (required)
* `TAVILY_API_KEY`: Your Tavily API key for web search (required)
* `CHAINLIT_AUTH_SECRET`: JWT secret for authentication (required) - Generate with `chainlit create-secret`
* `LANGSMITH_API_KEY`: Your LangSmith API key (optional, for tracing)
* `LANGSMITH_TRACING`: Whether to enable tracing (default: false)
* `LANGSMITH_ENDPOINT`: The LangSmith endpoint
* `LANGSMITH_PROJECT`: The LangSmith project name

## Dependencies

Key dependencies installed:

- `langgraph`: Core graph framework
- `langgraph-checkpoint-sqlite`: SQLite-based persistent memory
- `aiosqlite`: Async SQLite support for checkpointing
- `langchain-openai`: OpenAI integration
- `langchain-community`: Community tools including Tavily search
- `chainlit`: Web UI framework with built-in authentication
- `python-dotenv`: Environment variable management

## File Structure

```
.
├── app.py                    # Main application file with LangGraph logic
├── chainlit.md              # Chainlit welcome message
├── .chainlit                # Chainlit configuration (auth enabled)
├── requirements.txt         # Python dependencies
├── .env.sample             # Example environment variables
├── .env                    # Your API keys (create this file)
├── checkpoints.db          # SQLite database for conversation memory (auto-created)
└── README.md               # This file
```

## Testing Memory and Authentication

To test that authentication and memory are working:

1. Start the application: `uv run chainlit run app.py`
2. Open browser to `http://localhost:8000`
3. Log in with **maria** / **guapo123**
4. Send a message: "My name is María"
5. Send another message: "What's my name?"
6. The AI should remember and respond with "María"
7. Log out and log in with **juan** / **fe123**
8. Ask "What's my name?" - Juan will have a fresh conversation
9. Send a message: "My name is Juan"
10. Log out and log back in as **maria** / **guapo123**
11. Ask "What's my name?" - María's conversation history is preserved
12. Each user maintains their own separate, persistent conversation

## Security Considerations

⚠️ **Important**: This implementation uses a simple in-memory user dictionary for demonstration purposes. For production use, you should:

1. **Password Security**:
   - Use proper password hashing (bcrypt, argon2, etc.)
   - Never store passwords in plain text
   - Implement password strength requirements

2. **User Management**:
   - Store users in a proper database (PostgreSQL, MySQL, etc.)
   - Implement user registration and password reset flows
   - Add email verification

3. **Authentication**:
   - Use secure session management
   - Implement rate limiting for login attempts
   - Add two-factor authentication (2FA) for sensitive applications

4. **Environment Variables**:
   - Never commit `.env` files to version control
   - Keep `CHAINLIT_AUTH_SECRET` secure and rotate it periodically
   - Use different secrets for development and production

## Troubleshooting

### Missing API Keys

If you get an error about missing API keys:
- Make sure you've created a `.env` file (not just `.env.sample`)
- Ensure your API keys are properly formatted in the `.env` file
- Check that the `.env` file is in the same directory as `app.py`

### Authentication Errors

If you get a "JWT secret required" error:
- Run `uv run chainlit create-secret` to generate a secret
- Add the generated secret to your `.env` file as `CHAINLIT_AUTH_SECRET`
- Restart the application

### Database Issues

If you encounter database errors:
- Delete the `checkpoints.db` file and restart the application
- The database will be recreated automatically

### Import Errors

If you see import errors:
- Make sure you've activated the virtual environment: `source .venv/bin/activate`
- Reinstall dependencies: `uv pip install -r requirements.txt`

## Contributing

Contributions to LangGraph are welcome. If you'd like to contribute, please follow these steps:

1. Fork the repository
2. Make your changes
3. Submit a pull request

## License

LangGraph is licensed under the MIT License.
