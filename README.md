# MCP SQL Client - Learning Model Context Protocol

A minimal educational example demonstrating the four core components of an MCP (Model Context Protocol) client that connects to a SQL server and enables natural language conversations with your database.

## 🎯 Project Purpose

This project was built to understand the fundamental architecture of MCP clients by creating a working example with the least amount of code possible. It demonstrates how Claude (or any LLM) can intelligently use SQL tools to answer questions about your database.

## 📁 Project Structure

```
MCP-MSSQL-SERVER/
├── src/mssql/server.py          # FastMCP SQL server (connects to MSSQL)
├── mcp_client.py                # FastMCP client (this is what we built)
├── .env                         # Environment variables (your credentials)
├── .env.example                 # Example environment variables template
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🏗️ Architecture Overview

The MCP client consists of exactly **4 core components** that work together:

```
User Input → [1. Transport] → [2. Tool Registry] → [3. Memory] → [4. Execution Engine] → Claude → SQL Results
```

## 🔧 The Four MCP Client Components

### 1. **Transport Layer** 
*Handles server connections*

```python
# Connect to FastMCP SQL server via stdio using relative path
client = Client("./src/mssql/server.py")
```

**What it does:**
- Establishes communication with the MCP server
- Uses stdio transport (standard input/output) to run the server as a subprocess
- FastMCP automatically infers the transport type from the file path

### 2. **Tool Registry**
*Tracks available server capabilities*

```python
# Lines 24-32: Get and format available SQL tools
tools = await client.list_tools()
print(f"Connected! Available tools: {[tool.name for tool in tools]}")

claude_tools = [
    {
        "name": tool.name,
        "description": tool.description, 
        "input_schema": tool.inputSchema or {}
    }
    for tool in tools
]
```

**What it does:**
- Discovers what tools the SQL server offers (`get_relationships`, `describe_table`, `execute_sql`)
- Formats tool definitions for Claude's function calling API
- Provides the "menu" of available database operations

### 3. **Memory**
*Conversation history as list of dictionaries*

```python
# Line 18: Simple conversation storage
conversation = []

# Line 42: Add user messages
conversation.append({"role": "user", "content": user_input})

# Line 71: Add assistant responses  
conversation.append({"role": "assistant", "content": assistant_content})
```

**What it does:**
- Stores conversation history in a Python list
- Each message is a dict with "role" (user/assistant) and "content"
- Sent to Claude with each request so it remembers context
- Grows throughout the conversation session

### 4. **Execution Engine** 
*LLM integration with tool context*

```python
# Lines 45-70: Claude decides which SQL tools to call
response = anthropic.messages.create(
    model=os.getenv("ANTHROPIC_MODEL"),
    max_tokens=1000,
    messages=conversation,        # Full conversation history
    tools=claude_tools           # Available SQL tools
)

# Handle Claude's tool calls
for content_block in response.content:
    if content_block.type == "tool_use":
        tool_name = content_block.name
        tool_args = content_block.input
        
        # Execute the actual SQL tool via MCP
        tool_result = await client.call_tool(tool_name, tool_args)
```

**What it does:**
- Sends user questions + conversation history + available tools to Claude
- Claude decides which SQL tools to use (if any)
- Executes the tools via MCP and returns real database results
- Combines Claude's intelligence with live database access

## 🔄 How It All Works Together

1. **User asks:** "What tables do I have?"

2. **Transport Layer:** Client connects to SQL server via stdio

3. **Tool Registry:** Discovers available tools: `execute_sql`, `describe_table`, `get_relationships`

4. **Memory:** Adds user question to conversation history

5. **Execution Engine:** 
   - Sends question + tools + history to Claude
   - Claude decides to call `execute_sql` with query `"SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES"`
   - Client executes the tool via MCP
   - Gets real table names from your database
   - Claude formats a nice response

6. **Memory:** Stores Claude's response for future context

## 🛠️ Setup Instructions

### Prerequisites

- Python 3.8+
- ODBC Driver 17/18 for SQL Server
- Access to a SQL Server database
- Anthropic API key

### Installing ODBC Driver

Before setting up the project, you need to install the Microsoft ODBC Driver for SQL Server:

**For macOS:**
```bash
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
brew update
brew install msodbcsql18 mssql-tools18
```

**For Ubuntu/Debian:**
```bash
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list > /etc/apt/sources.list.d/mssql-release.list
apt-get update
ACCEPT_EULA=Y apt-get install -y msodbcsql18 mssql-tools18
```

**For RHEL/CentOS:**
```bash
curl https://packages.microsoft.com/config/rhel/8/prod.repo > /etc/yum.repos.d/mssql-release.repo
ACCEPT_EULA=Y yum install -y msodbcsql18 mssql-tools18
```

**For Windows:**
Download and install from the [Microsoft Download Center](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

After installation, make sure to update the MSSQL_DRIVER value in your .env file to match the installed driver name.

### Installation

1. **Clone and setup virtual environment:**
```bash
git clone <your-repo>
cd MCP-MSSQL-SERVER
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables:**
```bash
cp .env.example .env
```
Then edit the `.env` file with your credentials:
```env
ANTHROPIC_API_KEY=your-claude-api-key
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
MSSQL_SERVER=your-server
MSSQL_DATABASE=your-database  
MSSQL_USER=your-username
MSSQL_PASSWORD=your-password
MSSQL_DRIVER={ODBC Driver 17 for SQL Server}
```

### Usage

```bash
python mcp_client.py
```

**Example conversation:**
```
You: What tables are in my database?
Bot: I'll check what tables are available in your database.

Tool result from execute_sql:
TABLE_NAME
Users
Orders  
Products

Based on the query results, your database contains 3 tables:
- Users
- Orders  
- Products

You: Show me the structure of the Users table
Bot: I'll describe the structure of the Users table for you.

Tool result from describe_table:
COLUMN_NAME,DATA_TYPE,IS_NULLABLE,COLUMN_DEFAULT,MAX_LENGTH,PRECISION,SCALE
id,int,NO,,,,
name,varchar,YES,,50,,
email,varchar,NO,,100,,

The Users table has the following structure:
- id: int, NOT NULL (primary key)
- name: varchar(50), NULL allowed  
- email: varchar(100), NOT NULL
```

## 🧠 Learning Concepts

### Why This Architecture?

1. **Separation of Concerns:** Each component has a single responsibility
2. **Modularity:** Components can be swapped (different LLMs, transports, memory stores)
3. **Scalability:** Easy to add more servers, tools, or capabilities
4. **Testability:** Each component can be tested independently

### Key MCP Concepts Demonstrated

- **Tools vs Resources:** This uses tools (functions Claude can call) rather than resources (static data)
- **Transport Independence:** Could easily switch from stdio to HTTP
- **Stateless Servers:** Server doesn't remember conversations; client handles memory
- **Function Calling:** LLM decides which tools to use based on natural language

### What Makes This "Minimal"?

- **~90 lines of code** total
- **No complex frameworks** beyond FastMCP
- **No databases** for conversation storage (just a Python list)
- **No web UI** (terminal-based)
- **Single file** client implementation

## 🚀 Extending This Example

Want to learn more? Try adding:

- **Multiple servers:** Weather API + SQL database
- **Different memory:** Vector database for semantic search
- **Better error handling:** Retry logic, graceful failures
- **Web interface:** FastAPI + HTML frontend
- **Streaming responses:** Real-time tool execution updates

## 📚 Additional Resources

- [FastMCP Documentation](https://fastmcp.com/)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [Anthropic Function Calling Guide](https://docs.anthropic.com/claude/docs/functions-external-tools)

## 🤝 Contributing

This is a learning project! Feel free to:
- Add more educational comments
- Create additional minimal examples
- Improve error messages
- Add more detailed logging

---

*Built for learning MCP architecture through hands-on implementation.*