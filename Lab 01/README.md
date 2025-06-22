# Lab 01: Building a Weather MCP Server

A practical implementation demonstrating how to build a functional MCP server that exposes weather data tools through the Model Context Protocol.

## 🎯 Project Purpose

This is the first lab in the MCP Training Series, designed to introduce the fundamental concepts of the Model Context Protocol through a practical implementation. It focuses on creating a working MCP server that provides weather data tools, allowing LLMs like Claude to access real-time weather information.

As the initial lab in the series, it establishes the foundation for understanding MCP architecture by demonstrating server-side implementation. The following labs will build on these concepts to explore client implementations and more advanced features.

## 📁 Project Structure

```
Lab 01/
├── client.py               # Simple MCP client implementation
├── weather.py              # Weather MCP server implementation (main focus)
├── pyproject.toml          # Python project dependencies
└── README.md               # This file
```

## 🏗️ Architecture Overview

The MCP server consists of **4 core components** that work together:

```
Client Request → [1. Transport] → [2. Tool Registry] → [3. Memory] → [4. Execution Engine] → Results → Client
```

## 🔧 The Four MCP Server Components

### 1. **Transport Layer**

_Handles client communications_

```python
# Configure and run server with stdio transport
mcp.run(transport='stdio')
```

**What it does:**
* Establishes communication channel with MCP clients
* Uses stdio transport (standard input/output) for simple subprocess communication
* FastMCP automatically handles the JSON-RPC protocol details

### 2. **Tool Registry**

_Defines available server capabilities_

```python
# Register tools with the MCP server
@mcp.tool()
async def get_alerts(state: str) -> str:
    """Get weather alerts for a US state.

    Args:
        state: Two-letter US state code (e.g. CA, NY)
    """
    # Tool implementation...
```

**What it does:**
* Defines the tools that clients can discover and use
* Provides schemas and documentation for each tool
* Makes tools available through the MCP protocol

### 3. **Memory**

_Server state management_

While this simple server doesn't implement explicit memory storage, the FastMCP framework maintains:
* Active connections
* Request/response correlation
* Server configuration state

In more complex servers, you might add:
* Caching of frequent requests
* User session data
* Rate limiting information

### 4. **Execution Engine**

_Implements the actual tool functionality_

```python
# Tool implementation
url = f"{NWS_API_BASE}/alerts/active/area/{state}"
data = await make_nws_request(url)

if not data or "features" not in data:
    return "Unable to fetch alerts or no alerts found."

alerts = [format_alert(feature) for feature in data["features"]]
return "\n---\n".join(alerts)
```

**What it does:**
* Contains the actual business logic for each tool
* Makes external API calls to the National Weather Service
* Formats responses for client consumption
* Handles errors gracefully

## 🔄 How It All Works Together

1. **Client connects** to the weather server using stdio transport
2. **Server initializes** and registers available tools
3. **Client discovers** the `get_alerts` and `get_forecast` tools
4. **User asks:** "What's the weather forecast for Seattle?"
5. **Client sends** the request to Claude with available tools
6. **Claude decides** to use the `get_forecast` tool with coordinates for Seattle
7. **Client executes** the tool via MCP
8. **Server receives** the tool call through the transport layer
9. **Tool registry** routes the call to the correct function
10. **Execution engine** calls the NWS API and formats the response
11. **Transport layer** sends the result back to the client
12. **Claude** receives the weather data and formats a natural language response

## 🛠️ Usage Instructions

### Running the Server

```bash
python weather.py
```

This starts the MCP server in stdio mode, ready to accept connections.

### Connecting with the Client

```bash
python client.py weather.py
```

This connects the MCP client to the weather server, allowing you to ask questions about weather alerts and forecasts.

### Example Conversation

```
Query: What weather alerts are active in CA?

[Calling tool get_alerts with args {'state': 'CA'}]

I checked for active weather alerts in California (CA). Here's what I found:

Event: Heat Advisory
Area: San Diego County Coastal Areas
Severity: Minor
Description: The National Weather Service has issued a Heat Advisory for San Diego County coastal areas. Temperatures are expected to reach 85-90°F near the coast and up to 95°F for inland coastal areas.
Instructions: Drink plenty of fluids, stay in air-conditioned rooms, and check on relatives and neighbors.

Event: Red Flag Warning
Area: Northern California Interior
Severity: Severe
Description: Critical fire weather conditions are expected due to strong winds and low humidity.
Instructions: Avoid outdoor burning and activities that could cause sparks.
```

## 🧠 Learning Concepts

### Key MCP Server Concepts Demonstrated

* **Tool Registration:** Defining functions that clients can discover and call
* **Input Validation:** Using Python type hints for parameter validation
* **Error Handling:** Gracefully handling API failures
* **Response Formatting:** Creating user-friendly output from raw API data
* **External API Integration:** Connecting to third-party services (NWS)

### What Makes This Implementation Special?

* **Real-world utility:** Provides genuinely useful weather information
* **API integration:** Shows how to wrap external APIs as MCP tools
* **Error resilience:** Handles network issues and API failures gracefully
* **Clean architecture:** Separates concerns into distinct components
* **Minimal dependencies:** Uses only what's needed for clarity

## 🚀 Extending This Example

Want to enhance this weather server? Try adding:

* **More weather data sources:** Add tools for different weather APIs
* **Geocoding:** Convert city names to coordinates automatically
* **Historical data:** Add tools to retrieve past weather information
* **Weather maps:** Generate and return weather map images
* **User preferences:** Store and apply user location preferences

## 📚 Additional Resources

* [FastMCP Documentation](https://github.com/anthropics/anthropic-sdk-python)
* [National Weather Service API](https://www.weather.gov/documentation/services-web-api)
* [Model Context Protocol Specification](https://docs.anthropic.com/claude/docs/model-context-protocol)

---

_Built for learning MCP architecture through hands-on implementation._
