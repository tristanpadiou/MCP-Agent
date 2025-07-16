from __future__ import annotations

from pydantic_ai import Agent

from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.mcp import MCPServerStreamableHTTP, MCPServerSSE, MCPServerStdio
from dataclasses import dataclass
from datetime import datetime
from pydantic import Field
import json
import os
from pathlib import Path
from pydantic_ai.messages import (
    ModelMessage,

)




@dataclass
class Api_keys:
    api_keys: dict


@dataclass
class Message_state:
    messages: list[ModelMessage]


    
    
class MCP_Agent:
   
    def __init__(self, api_keys:dict, mpc_server_urls:list = [], mpc_stdio_commands:list = [], instructions:str = None):
        """
        Args:
            
            api_keys (dict): The API keys to use as a dictionary
            mpc_server_urls (list): The list of dicts containing the url and the name
              of the mpc server and the type of connection, and the bearer token if necessary
              example:
              [
                {
                  'url': 'http://localhost:8000',
                  'name': 'mcp_server_1',
                  'type': 'http','SSE'
                  'headers': {'Authorization': 'Bearer', '1234567890'} #optional or None
                }
              ]
            mpc_stdio_commands (list): The list of commands to use with the stdio mpc server
              example:
              [
                {
                  'name': 'memory',
                  'command': 'npx', 'docker', 'npm', 'python'
                  'args': ['-y', '@modelcontextprotocol/server-memory'] 
                }
              ]
            
            instructions (str, optional): Instructions for the agent. If not provided, 
                                          defaults to the instructions in the config.json file.

            
        """
        
        # Load configuration
        self.instructions = instructions
        
        self.api_keys=Api_keys(api_keys=api_keys)
        
        self.mpc_server_urls = mpc_server_urls
        self.mpc_stdio_commands = mpc_stdio_commands
        
    
        
        # tools
        self.llms={'mcp_llm':OpenAIModel('gpt-4.1-mini',provider=OpenAIProvider(api_key=self.api_keys.api_keys['openai_api_key']))}
        
        
        #mpc servers
        self.mpc_servers=[]
        for mpc_server_url in self.mpc_server_urls:
            if mpc_server_url['type'] == 'http':
                if mpc_server_url['headers'] is not None:
                    self.mpc_servers.append(MCPServerStreamableHTTP(url=mpc_server_url['url'], headers=mpc_server_url['headers']))
                else:
                    self.mpc_servers.append(MCPServerStreamableHTTP(mpc_server_url['url']))
            elif mpc_server_url['type'] == 'SSE':
                if mpc_server_url['headers'] is not None:
                    self.mpc_servers.append(MCPServerSSE(url=mpc_server_url['url'], headers=mpc_server_url['headers']))
                else:
                    self.mpc_servers.append(MCPServerSSE(mpc_server_url['url']))
        for mpc_stdio_command in self.mpc_stdio_commands:
            self.mpc_servers.append(MCPServerStdio(command=mpc_stdio_command['command'], args=mpc_stdio_command['args']))

        self._mcp_context_manager = None
        self._is_connected = False
        #agent

        self.agent=Agent(self.llms['mcp_llm'],tools=[], mcp_servers=self.mpc_servers, instructions=self.instructions)
        self.memory=Message_state(messages=[])
        
    
    async def connect(self):
        """Establish persistent connection to MCP server"""
        if not self._is_connected:
            self._mcp_context_manager = self.agent.run_mcp_servers()
            await self._mcp_context_manager.__aenter__()
            self._is_connected = True
            return "Connected to MCP server"

    async def disconnect(self):
        """Close the MCP server connection"""
        if self._is_connected and self._mcp_context_manager:
            await self._mcp_context_manager.__aexit__(None, None, None)
            self._is_connected = False
            self._mcp_context_manager = None
            return "Disconnected from MCP server"
    async def chat(self, query:any):
        """
        # Chat Function Documentation

        This function enables interaction with the user through various types of input.

        
        The message_history of Agent can be accessed using the following code:
        ```python
        
        agent.memory.messages
        ```
        """
        if not self._is_connected:
            await self.connect()
            
        result=await self.agent.run(query, message_history=self.memory.messages)
        self.memory.messages=result.all_messages()
        return result.output
    
    
    
    def reset(self):
        """
        Resets the Agent to its initial state.

        Returns:
            str: A confirmation message indicating that the agent has been reset.
        """
        self.memory.messages=[]
        return f'Agent has been reset'
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()
