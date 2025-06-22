import asyncio
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from anthropic import Anthropic
from dotenv import load_dotenv

"""
Model Context Protocol (MCP) Client Implementation

MCP CLIENT CORE COMPONENTS:
1. Transport - Handles communication with the MCP server (e.g., stdio, HTTP/SSE)
2. Tool Registry - Manages available tools and their schemas
3. Memory - Maintains state and context across interactions
4. Execution Engine - Coordinates tool execution and result handling

These components work together in the flow:
User Input → Transport → Tool Registry → Memory → Execution Engine → LLM → Results
"""

load_dotenv()  # load environment variables from .env

class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        # [COMPONENT: Memory] - Initialize session state
        self.session: Optional[ClientSession] = None
        # [COMPONENT: Memory] - Resource management for maintaining state
        self.exit_stack = AsyncExitStack()
        # LLM client for processing queries
        self.anthropic = Anthropic()

    async def connect_to_server(self, server_script_path: str):
        """Connect to an MCP server
        
        Args:
            server_script_path: Path to the server script (.py or .js)
        """
        # [COMPONENT: Transport] - Determine which transport to use based on file type
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")
            
        command = "python" if is_python else "node"
        # [COMPONENT: Transport] - Configure transport parameters
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None
        )
        
        # [COMPONENT: Transport] - Establish connection using stdio transport
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        # [COMPONENT: Memory] - Create client session with transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        
        # [COMPONENT: Transport] - Perform initialization handshake
        await self.session.initialize()
        
        # [COMPONENT: Tool Registry] - List and register available tools from the server
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    async def process_query(self, query: str) -> str:
        """Process a query using Claude and available tools"""
        # [COMPONENT: Memory] - Initialize conversation state
        messages = [
            {
                "role": "user",
                "content": query
            }
        ]

        # [COMPONENT: Tool Registry] - Get available tools for the LLM to use
        response = await self.session.list_tools()
        available_tools = [{ 
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.inputSchema
        } for tool in response.tools]

        # Initial Claude API call
        response = self.anthropic.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=messages,
            tools=available_tools
        )

        # [COMPONENT: Execution Engine] - Process response and handle tool calls
        tool_results = []
        final_text = []

        for content in response.content:
            if content.type == 'text':
                final_text.append(content.text)
            elif content.type == 'tool_use':
                tool_name = content.name
                tool_args = content.input
                
                # [COMPONENT: Execution Engine] - Execute tool call through MCP session
                result = await self.session.call_tool(tool_name, tool_args)
                tool_results.append({"call": tool_name, "result": result})
                final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")

                # [COMPONENT: Memory] - Update conversation with tool results
                if hasattr(content, 'text') and content.text:
                    messages.append({
                      "role": "assistant",
                      "content": content.text
                    })
                messages.append({
                    "role": "user", 
                    "content": result.content
                })

                # Get next response from Claude
                response = self.anthropic.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    messages=messages,
                )

                final_text.append(response.content[0].text)

        return "\n".join(final_text)

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")
        
        while True:
            try:
                query = input("\nQuery: ").strip()
                
                if query.lower() == 'quit':
                    break
                    
                response = await self.process_query(query)
                print("\n" + response)
                    
            except Exception as e:
                # [COMPONENT: Execution Engine] - Error handling
                print(f"\nError: {str(e)}")
    
    async def cleanup(self):
        """Clean up resources"""
        # [COMPONENT: Memory] - Proper resource cleanup
        await self.exit_stack.aclose()

async def main():
    if len(sys.argv) < 2:
        print("Usage: python client.py <path_to_server_script>")
        sys.exit(1)
        
    client = MCPClient()
    try:
        # [COMPONENT: Transport] - Connect to server and establish session
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        # [COMPONENT: Memory] - Ensure cleanup happens even on errors
        await client.cleanup()

if __name__ == "__main__":
    import sys
    asyncio.run(main())