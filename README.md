# MCP-Agent

A Model Context Protocol (MCP) agent with a Gradio frontend that enables real-time streaming conversations.

## Features

- 🤖 **MCP-Enabled AI Agent**: Powered by pydantic-ai with MCP server integration
- 💬 **Interactive Chat Interface**: Real-time response handling in Gradio
- 🔧 **Configurable MCP Servers**: Support for HTTP and SSE MCP server connections
- 🎛️ **Interactive UI**: Easy-to-use configuration and chat management
- 📱 **Responsive Design**: Clean, modern chat interface

## Quick Start

### Prerequisites

Install [uv](https://docs.astral.sh/uv/) - the fast Python package manager:

```bash
# On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or via package managers
# macOS: brew install uv
# Linux: pip install uv
```

### 1. Install Dependencies

```bash
# Install all dependencies using uv
uv sync
```

This will create a virtual environment and install all required packages.

### 2. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
# Required: OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Add other API keys as needed
```

Alternatively, you can set environment variables directly:

```bash
export OPENAI_API_KEY="your_openai_api_key_here"
```

### 3. Run the Gradio App

```bash
# Run the app using uv
uv run python -m src.gradio_app.app
```

The app will open in your browser at `http://localhost:7860`

## How to Use

1. **Initialize the Agent**: 
   - Enter your OpenAI API key in the sidebar
   - Optionally configure MCP servers
   - Click "🚀 Initialize Agent"
2. **Start Chatting**: Type your message in the chat input
3. **View Responses**: See responses from the AI in the chat interface
4. **Reset Chat**: Use "🔄 Reset Chat" to clear conversation history
5. **Disconnect**: Use "🔌 Disconnect Agent" to disconnect from MCP servers

## MCP Server Configuration

The agent supports connecting to MCP servers for extended functionality:

1. Use the sidebar "🌐 MCP Servers" section
2. Add server details:
   - **Server URL**: e.g., `http://localhost:8000`
   - **Server Name**: Custom name for the server
   - **Connection Type**: Choose between HTTP or SSE
   - **Headers**: Optional authentication headers (e.g., `Authorization: Bearer token`)
3. Click "Add Server" to configure additional servers (up to 3)
4. Initialize the agent to apply changes

## Development

### Adding Dependencies

```bash
# Add a new dependency
uv add requests

# Add a development dependency
uv add --dev pytest

# Remove a dependency
uv remove requests
```

### Running Tests

```bash
# Run tests (if you have any)
uv run pytest

# Run with coverage
uv run pytest --cov=src
```

### Code Formatting

```bash
# Format code with black
uv run black src/

# Check with flake8
uv run flake8 src/

# Type checking with mypy
uv run mypy src/
```

## Project Structure

```
MCP-Agent/
├── src/
│   ├── __init__.py
│   ├── gradio_app/
│   │   ├── __init__.py
│   │   └── app.py          # Gradio chatbot frontend
│   └── mcp_agent/
│       ├── __init__.py
│       └── agent.py        # Core MCP agent implementation
├── notebooks/
│   └── test.ipynb          # Jupyter notebook for testing
├── pyproject.toml         # Project configuration and dependencies
├── uv.lock               # Lock file for reproducible builds
├── README.md             # This file
└── DEPLOY.md             # Deployment instructions
```

## API Usage

You can also use the agent programmatically:

```python
import asyncio
from src.mcp_agent.agent import MCP_Agent

# Initialize agent
api_keys = {"openai_api_key": "your_key_here"}
agent = MCP_Agent(api_keys=api_keys)

# Use as async context manager
async def chat_example():
    async with agent:
        response = await agent.chat("Hello, how can you help me?")
        print(response)

# Or manage connections manually
async def manual_example():
    await agent.connect()
    response = await agent.chat("What can you do?")
    print(response)
    await agent.disconnect()

# Run the async function
asyncio.run(chat_example())
```

## Streaming Responses

The agent supports streaming for real-time response generation:

```python
async def stream_example():
    async with agent:
        async for chunk in agent.stream("Tell me a story"):
            print(chunk, end="", flush=True)
```

## Dependencies

- **gradio**: Web app framework
- **pydantic-ai**: AI agent framework with MCP support
- **openai**: OpenAI API client (included in pydantic-ai)
- **pydantic**: Data validation and settings management

All dependencies are managed by `uv` and specified in `pyproject.toml`.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Install dependencies: `uv sync`
4. Make your changes
5. Test thoroughly: `uv run pytest`
6. Format code: `uv run black src/`
7. Submit a pull request

## License

This project is open source. Please check the license file for details.

## Troubleshooting

### Common Issues

1. **Agent won't initialize**: Check that your OpenAI API key is correctly set
2. **MCP server connection fails**: Verify server URL and authentication details
3. **Import errors**: Ensure you're running from the project root directory with `uv run`
4. **Virtual environment issues**: Try `uv sync` to recreate the environment

### Environment Setup

For different environments, you can set the API key via:

- **Environment variable**: `export OPENAI_API_KEY="your_key"`
- **Direct configuration**: Enter the API key in the Gradio interface

### Development Environment

```bash
# Activate the virtual environment manually (optional)
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate     # On Windows

# Or always use uv run (recommended)
uv run python script.py
```

## Support

If you encounter issues or have questions, please open an issue on the GitHub repository.
