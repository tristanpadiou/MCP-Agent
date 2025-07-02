# MCP-Agent

A Model Context Protocol (MCP) agent with a Streamlit frontend that enables real-time streaming conversations.

## Features

- 🤖 **MCP-Enabled AI Agent**: Powered by pydantic-ai with MCP server integration
- 💬 **Streaming Chat Interface**: Real-time response streaming in Streamlit
- 🔧 **Configurable MCP Servers**: Support for HTTP and SSE MCP server connections
- 🎛️ **Interactive UI**: Easy-to-use sidebar configuration and chat management
- 📱 **Responsive Design**: Clean, modern chat interface

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

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

### 3. Run the Streamlit App

```bash
streamlit run streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

## How to Use

1. **Initialize the Agent**: Click "🚀 Initialize Agent" in the sidebar
2. **Start Chatting**: Type your message in the chat input at the bottom
3. **Watch Responses Stream**: See real-time streaming responses from the AI
4. **Reset Chat**: Use "🔄 Reset Chat" to clear conversation history

## MCP Server Configuration

The agent supports connecting to MCP servers for extended functionality:

1. Use the sidebar "🌐 MCP Servers" section
2. Add server details:
   - **Server URL**: e.g., `http://localhost:8000`
   - **Connection Type**: Choose between HTTP or SSE
   - **Bearer Token**: Optional authentication token
3. Reinitialize the agent to apply changes

## Project Structure

```
MCP-Agent/
├── agent.py           # Core MCP agent implementation
├── streamlit_app.py   # Streamlit chatbot frontend
├── requirements.txt   # Python dependencies
├── README.md         # This file
└── test.ipynb        # Jupyter notebook for testing
```

## API Usage

You can also use the agent programmatically:

```python
import asyncio
from agent import MCP_Agent

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

- **streamlit**: Web app framework
- **pydantic-ai**: AI agent framework with MCP support
- **openai**: OpenAI API client
- **pydantic**: Data validation and settings management

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source. Please check the license file for details.

## Troubleshooting

### Common Issues

1. **Agent won't initialize**: Check that your OpenAI API key is correctly set
2. **Streaming not working**: Ensure you have a stable internet connection
3. **MCP server connection fails**: Verify server URL and authentication details

### Environment Setup

For different environments, you can set the API key via:

- **Environment variable**: `export OPENAI_API_KEY="your_key"`
- **Streamlit secrets**: Create `.streamlit/secrets.toml` with `OPENAI_API_KEY = "your_key"`
- **Direct configuration**: Modify the `initialize_agent()` function

## Support

If you encounter issues or have questions, please open an issue on the GitHub repository.
