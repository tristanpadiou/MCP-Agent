import streamlit as st
import asyncio
import os
from agent import MCP_Agent
import json

# Page configuration
st.set_page_config(
    page_title="MCP Agent Chatbot",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent" not in st.session_state:
    st.session_state.agent = None
if "agent_connected" not in st.session_state:
    st.session_state.agent_connected = False
if "mcp_servers" not in st.session_state:
    st.session_state.mcp_servers = []

def initialize_agent():
    """Initialize the MCP agent with API keys and server configuration"""
    try:
        # Get API keys from environment variables or Streamlit secrets
        api_keys = {}
        
        # Try to get from Streamlit secrets first
        try:
            api_keys['openai_api_key'] = st.secrets["openai_api_key"]
        except:
            # Fallback to environment variable
            api_keys['openai_api_key'] = os.getenv("openai_api_key")
        
        if not api_keys['openai_api_key']:
            st.error("OpenAI API key not found. Please set OPENAI_API_KEY in your environment variables or Streamlit secrets.")
            return None
        
        # Use MCP servers from session state
        mcp_servers = st.session_state.mcp_servers
        
        # Initialize agent
        agent = MCP_Agent(api_keys=api_keys, mpc_server_urls=mcp_servers)
        
        # Show configured servers info without testing connections
        if mcp_servers:
            st.success(f"✅ Agent initialized with {len(mcp_servers)} MCP server(s) configured")
            st.info("MCP server connections will be established when needed during chat.")
        else:
            st.success("✅ Agent initialized (no MCP servers configured)")
        
        return agent
        
    except Exception as e:
        st.error(f"Error initializing agent: {str(e)}")
        return None

def run_async_stream(agent: MCP_Agent, query: str):
    """Get response from agent and return it directly"""
    import asyncio
    import sys
    
    # async def get_response():
    #     """Get complete response using agent.chat"""
    #     try:
    #         response = await 
    #         return str(response)
    #     except Exception as e:
    #         return f"Error: {str(e)}"
    
    # Run with Windows compatibility
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    try:
        # Get and return the complete response
        response = asyncio.run(agent.chat(query))
        yield response
            
    except Exception as e:
        yield f"Error in execution: {str(e)}"

# Main app
def main():
    st.title("🤖 MCP Agent Chatbot")
    st.markdown("Chat with your MCP-enabled AI agent!")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Agent status
        if st.session_state.agent is not None:
            st.success("✅ Agent initialized")
            if st.session_state.agent_connected:
                st.success("🔗 Connected to MCP servers")
            else:
                st.info("📡 Ready to connect")
        else:
            st.warning("⚠️ Agent not initialized")
        
        # Initialize/Reset agent
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚀 Initialize Agent"):
                with st.spinner("Initializing agent..."):
                    st.session_state.agent = initialize_agent()
                    if st.session_state.agent:
                        st.success("Agent initialized successfully!")
                        st.rerun()
        
        with col2:
            if st.button("🔄 Reset Chat"):
                if st.session_state.agent:
                    st.session_state.agent.reset()
                st.session_state.messages = []
                st.success("Chat reset!")
                st.rerun()
        
        # MCP Server Configuration
        st.subheader("🌐 MCP Servers")
        
        # Display configured servers
        if st.session_state.mcp_servers:
            st.write("**Configured Servers:**")
            for i, server in enumerate(st.session_state.mcp_servers):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"• {server.get('name', 'Unnamed')} - {server.get('url', 'No URL')}")
                with col2:
                    if st.button("🗑️", key=f"delete_{i}", help="Delete server"):
                        st.session_state.mcp_servers.pop(i)
                        st.rerun()
        else:
            st.info("No MCP servers configured")
        
        with st.expander("Add MCP Server"):
            server_url = st.text_input("Server URL", placeholder="http://localhost:8000")
            server_name = st.text_input("Server Name", placeholder="my_mcp_server")
            server_type = st.selectbox("Connection Type", ["http", "SSE"])
            bearer_token = st.text_input("Bearer Token (optional)", type="password")
            
            if st.button("Add Server"):
                if server_url and server_name:
                    # Create server configuration object
                    server_config = {
                        "name": server_name,
                        "url": server_url,
                        "type": server_type,
                        "bearer_token": bearer_token if bearer_token else None
                    }
                    
                    # Add to session state
                    st.session_state.mcp_servers.append(server_config)
                    st.success(f"Added server: {server_name}")
                    st.rerun()
                else:
                    st.error("Please provide both server URL and name")
        
        st.markdown("---")
        st.markdown("### 📝 Instructions")
        st.markdown("""
        1. **Configure MCP Servers**: Add your MCP servers using the configuration section above
        2. **Initialize Agent**: Click to set up the MCP agent with your server configurations
        3. **Start Chatting**: Type your message and press Enter
        4. **Get Responses**: Complete responses appear when ready
        5. **Reset Chat**: Clear conversation history
        """)
    
    # Check if agent is initialized
    if st.session_state.agent is None:
        st.warning("⚠️ Please initialize the agent using the sidebar before starting to chat.")
        return
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("What would you like to know?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate assistant response
        with st.chat_message("assistant"):
            try:
                # Get the complete response
                response = ""
                for chunk in run_async_stream(st.session_state.agent, prompt):
                    response = chunk  # Since we're only yielding one complete response
                
                # Display the response
                st.markdown(response)
                
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                error_message = f"Sorry, I encountered an error: {str(e)}"
                st.error(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})

if __name__ == "__main__":
    main()
