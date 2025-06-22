# Lab 02: SQL Database Access with MCP

This lab demonstrates how to build an MCP client that connects to a SQL database server, enabling natural language interactions with your database.

## Overview

The SQL Database Client demonstrates:

1. Creating an MCP client that connects to a SQL database server
2. Using Claude to translate natural language queries into SQL
3. Executing SQL queries and returning formatted results
4. Implementing security measures for database access

## Architecture

This implementation consists of two main components:

1. **SQL MCP Server** (`src/mssql/server.py`): A FastMCP server that provides tools for database interaction
2. **MCP Client** (`mcp_client.py`): A client application that connects to the server and Claude

## Key Features

- **Read-only Database Access**: All queries are validated to ensure they are read-only
- **Table Exploration**: List tables, describe structure, view relationships
- **Natural Language Interface**: Ask questions about your data in plain English
- **Security**: SQL injection prevention and read-only access

## Setup

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file based on `.env.example` with your database credentials and Anthropic API key
4. Run the client: `python mcp_client.py`

## Example Usage

Once running, you can ask questions like:

- "What tables are available in the database?"
- "Show me the structure of the Customers table"
- "Find all orders placed in the last month"
- "What are the relationships between the Orders and Products tables?"

## Implementation Details

### MCP Server

The server exposes several tools:

- `execute_sql`: Run SQL queries against the database
- `describe_table`: Get detailed information about table structure
- `get_relationships`: View foreign key relationships

### MCP Client

The client demonstrates:

1. **Transport Layer**: Connection to the FastMCP SQL server
2. **Memory**: Simple conversation history management
3. **Tool Registry**: Discovery and formatting of available SQL tools
4. **Execution Engine**: Coordination between Claude and SQL tools

## Security Considerations

- The server validates all SQL queries to ensure they are read-only
- Queries are checked for SQL injection patterns
- Database credentials are stored in environment variables, not in code
- Connection is configured as read-only at the driver level

## Next Steps

Possible enhancements:

- Add support for data visualization
- Implement more sophisticated memory management
- Add authentication for the MCP server
- Support for multiple database types (PostgreSQL, MySQL, etc.)