import asyncio
import os
from fastmcp import Client
from anthropic import Anthropic
from dotenv import load_dotenv

# Step 0: Load environment variables from .env file
load_dotenv()

async def main():
    # ===========================================
    # 1. TRANSPORT LAYER - Connect to FastMCP SQL server  
    # ===========================================
    # Step 1.1: Initialize client with server path
    # Best practice: Use absolute paths for reliability
    client = Client("./src/mssql/server.py")
    # Could improve: client = Client(os.path.join(os.path.dirname(__file__), "src/mssql/server.py"))
    
    # ===========================================
    # 2. MEMORY - Conversation history as list of dicts
    # ===========================================
    # Step 2.1: Initialize simple in-memory conversation store
    # Could improve: Use a more persistent storage solution for production
    conversation = []
    
    # Step 2.2: Initialize Claude client with API key
    # Best practice: Get API key from environment variables
    anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    # Step 2.3: Use async context manager for proper connection lifecycle
    # Best practice: Using async with for connection management
    async with client:
        # ===========================================
        # 3. TOOL REGISTRY - Get available SQL tools
        # ===========================================
        # Step 3.1: Discover available tools from the server
        tools = await client.list_tools()
        print(f"Connected! Available tools: {[tool.name for tool in tools]}")
        
        # Step 3.2: Format tools for Claude's function calling API
        # Best practice: Transform MCP tool schemas to Claude's expected format
        claude_tools = [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema or {}
            }
            for tool in tools
        ]
        
        print("SQL Chat Ready! Type 'quit' to exit.")
        
        # ===========================================
        # 4. EXECUTION ENGINE - Chat loop with Claude + MCP tools
        # ===========================================
        # Step 4.1: Main conversation loop
        while True:
            user_input = input("\nYou: ")
            if user_input.lower() == 'quit':
                break
            
            # Step 4.2: Add user message to memory
            conversation.append({"role": "user", "content": user_input})
            
            try:
                # Step 4.3: Call Claude with tools available
                # Best practice: Using environment variable for model name
                response = anthropic.messages.create(
                    model=os.getenv("ANTHROPIC_MODEL"),
                    max_tokens=1000,
                    messages=conversation,
                    tools=claude_tools
                )
                
                # Step 4.4: Process Claude's response and handle tool calls
                # Could improve: Add streaming support for real-time responses
                assistant_content = ""
                
                for content_block in response.content:
                    if content_block.type == "text":
                        assistant_content += content_block.text
                    elif content_block.type == "tool_use":
                        # Step 4.5: Execute the FastMCP tool
                        tool_name = content_block.name
                        tool_args = content_block.input
                        
                        print(f"Calling tool: {tool_name} with {tool_args}")
                        
                        # Step 4.6: Call the actual FastMCP tool
                        # Could improve: Add error handling for specific tool failures
                        tool_result = await client.call_tool(tool_name, tool_args)
                        
                        # Step 4.7: Add tool result to conversation
                        assistant_content += f"\n\nTool result from {tool_name}:\n"
                        assistant_content += tool_result[0].text
                
                # Step 4.8: Add assistant response to memory
                conversation.append({"role": "assistant", "content": assistant_content})
                
                print(f"Bot: {assistant_content}")
                print(f"[Memory: {len(conversation)} messages]")
                
            except Exception as e:
                # Step 4.9: Basic error handling
                # Could improve: Add more specific error handling for different error types
                print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())