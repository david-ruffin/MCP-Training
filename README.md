# MCP Training Series

A comprehensive educational series for learning the Model Context Protocol (MCP) through hands-on examples. This repository contains progressive labs that teach MCP concepts and implementation through practical exercises.

## 🎯 Series Purpose

This training series helps developers understand and implement the Model Context Protocol (MCP) through practical, working examples. Each lab builds upon the concepts of the previous one, demonstrating how to leverage MCP to connect LLMs like Claude with external tools and data sources.

## 📚 Labs Overview

### Lab 01: Building a Weather MCP Server
A practical implementation demonstrating how to build a functional MCP server that exposes weather data tools through the Model Context Protocol.

**Key Concepts:**
- Creating an MCP server with FastMCP
- Implementing tool definitions and execution
- Connecting to external APIs (Weather service)
- Understanding server-side MCP components

### Lab 02: SQL Database Client
A minimal educational example demonstrating an MCP client that connects to a SQL server and enables natural language conversations with your database.

**Key Concepts:**
- Building an MCP client from scratch
- SQL database integration
- Tool discovery and execution
- Conversation memory management

## 🏗️ MCP Architecture Overview

All examples in this series follow the standard MCP architecture with 4 core components:

```
User Input → [1. Transport] → [2. Tool Registry] → [3. Memory] → [4. Execution Engine] → Claude → Results
```

1. **Transport Layer**: Handles communication between client and server
2. **Tool Registry**: Manages available tools and their schemas
3. **Memory**: Maintains state and context across interactions
4. **Execution Engine**: Coordinates tool execution and result handling

## 🛠️ Learning Path

This series is designed as a progressive learning journey:

1. **Lab 01**: Learn how to create an MCP server that provides weather data tools
2. **Lab 02**: Build a client that connects to a SQL database through MCP
3. **Future Labs**: More advanced topics will be added in subsequent labs

Each lab is self-contained with its own README and setup instructions, but concepts build progressively through the series.

## 🚀 Getting Started

```bash
# Clone this repository
git clone https://github.com/your-username/MCP-Training.git
cd MCP-Training

# Navigate to a specific lab
cd Lab\ 01
# Follow the lab-specific README instructions
```

## 📚 Additional Resources

- [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
- [Anthropic Claude Documentation](https://docs.anthropic.com/)
- [FastMCP Documentation](https://fastmcp.com/)

---

*Built for learning MCP architecture through hands-on implementation.*