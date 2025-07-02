import gradio as gr
import asyncio
import json
import atexit
import signal
import sys
from agent import MCP_Agent

class GradioMCPApp:
    def __init__(self):
        self.agent = None
        self.chat_history = []
        self._loop = None
        self.server_count = 1
        
    def get_or_create_loop(self):
        """Get existing event loop or create a new one"""
        if self._loop is None or self._loop.is_closed():
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
        return self._loop
        
    async def initialize_agent(self, openai_api_key, *server_configs):
        """Initialize the MCP Agent with provided configuration"""
        try:
            # Clean up existing agent first
            if self.agent:
                await self.disconnect_agent()
            
            # Build MCP servers configuration from form fields
            # server_configs comes as a flat list: [url1, name1, type1, token1, url2, name2, type2, token2, ...]
            mcp_servers = []
            for i in range(0, len(server_configs), 4):
                if i + 3 < len(server_configs):
                    server_url = server_configs[i]
                    server_name = server_configs[i + 1]
                    server_type = server_configs[i + 2]
                    bearer_token = server_configs[i + 3]
                    
                    if server_url and server_url.strip():
                        server_config = {
                            'url': server_url.strip(),
                            'name': server_name.strip() if server_name and server_name.strip() else f'server_{i//4 + 1}',
                            'type': server_type if server_type else 'http',
                            'bearer_token': bearer_token.strip() if bearer_token and bearer_token.strip() else None
                        }
                        mcp_servers.append(server_config)
            
            # Initialize agent
            api_keys = {'openai_api_key': openai_api_key}
            self.agent = MCP_Agent(api_keys=api_keys, mpc_server_urls=mcp_servers)
            
            # Connect to MCP servers
            await self.agent.connect()
            
            server_count = len(mcp_servers)
            if server_count == 0:
                return True, "Agent initialized successfully (no MCP servers configured)!"
            else:
                return True, f"Agent initialized successfully with {server_count} MCP server(s)!"
            
        except Exception as e:
            return False, f"Error initializing agent: {str(e)}"
    
    async def chat_with_agent(self, message):
        """Handle text chat with the agent"""
        if not self.agent:
            return self.chat_history, "Please initialize the agent first by providing your OpenAI API key and clicking 'Initialize Agent'."
        
        if not message or not message.strip():
            return self.chat_history, "Please provide a message."
        
        try:
            # Get response from agent
            response = await self.agent.chat(message.strip())
            
            # Update chat history
            self.chat_history.append([message.strip(), str(response)])
            
            return self.chat_history, ""
            
        except Exception as e:
            error_msg = f"Error during chat: {str(e)}"
            self.chat_history.append([message, error_msg])
            return self.chat_history, error_msg
    
    async def reset_agent(self):
        """Reset the agent's conversation history"""
        if self.agent:
            self.agent.reset()
            self.chat_history = []
            return [], "Agent conversation history reset successfully!"
        else:
            return [], "No agent to reset. Please initialize the agent first."
    
    async def disconnect_agent(self):
        """Disconnect from MCP servers"""
        if self.agent:
            try:
                await self.agent.disconnect()
            except Exception as e:
                print(f"Error during disconnect: {e}")
            finally:
                self.agent = None
                self.chat_history = []
        return [], "Agent disconnected successfully!"
    
    async def cleanup(self):
        """Clean up resources"""
        if self.agent:
            await self.disconnect_agent()
        if self._loop and not self._loop.is_closed():
            self._loop.close()

# Create the app instance
app_instance = GradioMCPApp()

def run_async_safely(coro, *args):
    """Safely run async function with proper error handling"""
    loop = app_instance.get_or_create_loop()
    try:
        return loop.run_until_complete(coro(*args))
    except Exception as e:
        print(f"Error in async operation: {e}")
        return None, f"Error: {str(e)}"

# Define async wrapper functions for Gradio
def initialize_agent_wrapper(openai_api_key, *server_configs):
    success, message = run_async_safely(
        app_instance.initialize_agent, 
        openai_api_key, *server_configs
    )
    if success is None:
        return gr.update(visible=False), gr.update(visible=True), message
    return gr.update(visible=success), gr.update(visible=not success), message

def chat_wrapper(message):
    chat_history, error_msg = run_async_safely(app_instance.chat_with_agent, message)
    if chat_history is None:
        return [], error_msg, ""
    return chat_history, error_msg, ""  # Clear input

def reset_wrapper():
    chat_history, message = run_async_safely(app_instance.reset_agent)
    if chat_history is None:
        return [], message
    return chat_history, message

def disconnect_wrapper():
    chat_history, message = run_async_safely(app_instance.disconnect_agent)
    if chat_history is None:
        return [], gr.update(visible=False), gr.update(visible=True), message
    return chat_history, gr.update(visible=False), gr.update(visible=True), message

# Cleanup function for graceful shutdown
def cleanup_on_exit():
    """Cleanup function to run on exit"""
    try:
        loop = app_instance.get_or_create_loop()
        if not loop.is_closed():
            loop.run_until_complete(app_instance.cleanup())
    except Exception as e:
        print(f"Error during cleanup: {e}")

# Register cleanup function
atexit.register(cleanup_on_exit)

# Handle SIGINT (Ctrl+C) gracefully
def signal_handler(signum, frame):
    print("\nReceived interrupt signal. Cleaning up...")
    cleanup_on_exit()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Server management functions
def add_server(current_count):
    """Show the next server configuration"""
    new_count = min(current_count + 1, 3)  # Max 3 servers
    return (
        new_count,
        gr.update(visible=new_count >= 2),  # server2_group
        gr.update(visible=new_count >= 3),  # server3_group
        gr.update(interactive=new_count < 3),  # add_server_btn
        gr.update(interactive=new_count > 1)   # remove_server_btn
    )

def remove_server(current_count):
    """Hide the last server configuration"""
    new_count = max(current_count - 1, 1)  # Min 1 server
    return (
        new_count,
        gr.update(visible=new_count >= 2),  # server2_group
        gr.update(visible=new_count >= 3),  # server3_group
        gr.update(interactive=new_count < 3),  # add_server_btn
        gr.update(interactive=new_count > 1)   # remove_server_btn
    )



# Create the Gradio interface
with gr.Blocks(title="MCP Agent Chat", theme=gr.themes.Soft()) as demo:
    with gr.Row():
        
        gr.Markdown("# MCP Agent Chat Interface")
        gr.HTML("")  # Balance spacing
    
  
    
    with gr.Sidebar():
        # Sidebar for configuration
        sidebar_column = gr.Column(scale=1, min_width=350)
        with sidebar_column:
            gr.Markdown("## 🔧 Configuration")
            
            openai_key = gr.Textbox(
                label="OpenAI API Key",
                type="password",
                placeholder="sk-...",
                info="Your OpenAI API key for the language model"
            )
            
            gr.Markdown("### MCP Servers Setup")
            gr.Markdown("Configure your MCP server connections (leave all URLs empty to run without MCP servers)")
            
            # Container for dynamic server configurations
            servers_container = gr.Column()
            
            # Initial server configuration
            with servers_container:
                # Server 1 (always present)
                with gr.Group():
                    gr.Markdown("#### Server 1")
                    server1_url = gr.Textbox(
                        label="Server URL",
                        placeholder="http://localhost:8000",
                        info="The URL of your MCP server"
                    )
                    server1_name = gr.Textbox(
                        label="Server Name",
                        placeholder="server_1",
                        info="A friendly name for your MCP server"
                    )
                    server1_type = gr.Dropdown(
                        label="Server Type",
                        choices=["http", "SSE"],
                        value="http",
                        info="The type of MCP server connection"
                    )
                    server1_token = gr.Textbox(
                        label="Bearer Token (Optional)",
                        type="password",
                        placeholder="Leave empty if not required",
                        info="Authentication token for the MCP server (if required)"
                    )
                
                # Server 2 (optional)
                server2_group = gr.Group(visible=False)
                with server2_group:
                    gr.Markdown("#### Server 2")
                    server2_url = gr.Textbox(
                        label="Server URL",
                        placeholder="http://localhost:8001",
                        info="The URL of your MCP server"
                    )
                    server2_name = gr.Textbox(
                        label="Server Name",
                        placeholder="server_2",
                        info="A friendly name for your MCP server"
                    )
                    server2_type = gr.Dropdown(
                        label="Server Type",
                        choices=["http", "SSE"],
                        value="http",
                        info="The type of MCP server connection"
                    )
                    server2_token = gr.Textbox(
                        label="Bearer Token (Optional)",
                        type="password",
                        placeholder="Leave empty if not required",
                        info="Authentication token for the MCP server (if required)"
                    )
                
                # Server 3 (optional)
                server3_group = gr.Group(visible=False)
                with server3_group:
                    gr.Markdown("#### Server 3")
                    server3_url = gr.Textbox(
                        label="Server URL",
                        placeholder="http://localhost:8002",
                        info="The URL of your MCP server"
                    )
                    server3_name = gr.Textbox(
                        label="Server Name",
                        placeholder="server_3",
                        info="A friendly name for your MCP server"
                    )
                    server3_type = gr.Dropdown(
                        label="Server Type",
                        choices=["http", "SSE"],
                        value="http",
                        info="The type of MCP server connection"
                    )
                    server3_token = gr.Textbox(
                        label="Bearer Token (Optional)",
                        type="password",
                        placeholder="Leave empty if not required",
                        info="Authentication token for the MCP server (if required)"
                    )
            
            # Server management buttons
            with gr.Row():
                add_server_btn = gr.Button("+ Add Server", variant="secondary", size="sm")
                remove_server_btn = gr.Button("- Remove Server", variant="secondary", size="sm", interactive=False)
            
            # Track current server count
            server_count_state = gr.State(1)
            
            init_btn = gr.Button("Initialize Agent", variant="primary", size="lg")
            init_status = gr.Textbox(label="Status", interactive=False, max_lines=3)
    
    # Main chat area
    chat_column = gr.Column(scale=2)
    with chat_column:
        with gr.Row():
            gr.Markdown("## 💬 Chat with your MCP Agent")
            config_status = gr.Markdown("", visible=False)  # Status when sidebar is collapsed
        
        chat_interface = gr.Column(visible=False)
        with chat_interface:
            chatbot = gr.Chatbot(
                label="Conversation",
                height=500,
                show_copy_button=True,
                avatar_images=("👤", "🤖")
            )
            
            with gr.Row():
                msg = gr.Textbox(
                    label="Message",
                    placeholder="Type your message here...",
                    scale=4,
                    lines=2
                )
                send_btn = gr.Button("Send", variant="primary", scale=1)
            
            error_display = gr.Textbox(
                label="Error Messages",
                visible=False,
                interactive=False
            )
            
            with gr.Row():
                reset_btn = gr.Button("Reset Conversation", variant="secondary")
                disconnect_btn = gr.Button("Disconnect Agent", variant="secondary")
        
        # Placeholder when agent is not initialized
        placeholder = gr.Markdown(
            "### 👋 Welcome!\n\nPlease configure and initialize your MCP Agent using the sidebar to start chatting.",
            visible=True
        )

    
    # Server management event handlers
    add_server_btn.click(
        fn=add_server,
        inputs=[server_count_state],
        outputs=[server_count_state, server2_group, server3_group, add_server_btn, remove_server_btn]
    )
    
    remove_server_btn.click(
        fn=remove_server,
        inputs=[server_count_state],
        outputs=[server_count_state, server2_group, server3_group, add_server_btn, remove_server_btn]
    )
    
    # Event handlers
    init_btn.click(
        fn=initialize_agent_wrapper,
        inputs=[
            openai_key,
            server1_url, server1_name, server1_type, server1_token,
            server2_url, server2_name, server2_type, server2_token,
            server3_url, server3_name, server3_type, server3_token
        ],
        outputs=[chat_interface, placeholder, init_status]
    )
    
    # Chat functionality
    def handle_chat(message):
        if not message or not message.strip():
            return app_instance.chat_history, "Please provide a message.", ""
        return chat_wrapper(message)
    
    send_btn.click(
        fn=handle_chat,
        inputs=[msg],
        outputs=[chatbot, error_display, msg]
    ).then(
        lambda error: gr.update(visible=bool(error)),
        inputs=[error_display],
        outputs=[error_display]
    )
    
    msg.submit(
        fn=handle_chat,
        inputs=[msg],
        outputs=[chatbot, error_display, msg]
    ).then(
        lambda error: gr.update(visible=bool(error)),
        inputs=[error_display],
        outputs=[error_display]
    )
    
    reset_btn.click(
        fn=reset_wrapper,
        outputs=[chatbot, error_display]
    ).then(
        lambda error: gr.update(visible=bool(error)),
        inputs=[error_display],
        outputs=[error_display]
    )
    
    disconnect_btn.click(
        fn=disconnect_wrapper,
        outputs=[chatbot, chat_interface, placeholder, init_status]
    )

if __name__ == "__main__":
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        show_error=True
    )
