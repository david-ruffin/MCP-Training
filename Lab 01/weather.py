from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

"""
Model Context Protocol (MCP) Server Implementation

MCP SERVER CORE COMPONENTS:
1. Transport - Handles communication with clients (e.g., stdio, HTTP/SSE)
2. Tool Registry - Defines and exposes available tools to clients
3. Memory - Maintains server state and context
4. Execution Engine - Implements the actual tool functionality

These components work together in the flow:
Client Request → Transport → Tool Registry → Execution Engine → Results → Transport → Client
"""

# [COMPONENT: Tool Registry] - Create FastMCP server instance with name
mcp = FastMCP("weather")

# Constants
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"

# [COMPONENT: Execution Engine] - Helper function with error handling
async def make_nws_request(url: str) -> dict[str, Any] | None:
    """Make a request to the NWS API with proper error handling."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

# [COMPONENT: Execution Engine] - Format tool output consistently
def format_alert(feature: dict) -> str:
    """Format an alert feature into a readable string."""
    props = feature["properties"]
    return f"""
Event: {props.get('event', 'Unknown')}
Area: {props.get('areaDesc', 'Unknown')}
Severity: {props.get('severity', 'Unknown')}
Description: {props.get('description', 'No description available')}
Instructions: {props.get('instruction', 'No specific instructions provided')}
"""

# [COMPONENT: Tool Registry] - Register tool with the MCP server
@mcp.tool()
async def get_alerts(state: str) -> str:
    """Get weather alerts for a US state.

    Args:
        state: Two-letter US state code (e.g. CA, NY)
    """
    # [COMPONENT: Execution Engine] - Implement tool functionality
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)

    # [COMPONENT: Execution Engine] - Handle API failures gracefully
    if not data or "features" not in data:
        return "Unable to fetch alerts or no alerts found."

    if not data["features"]:
        return "No active alerts for this state."

    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)

# [COMPONENT: Tool Registry] - Register another tool with the MCP server
@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """Get weather forecast for a location.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
    """
    # [COMPONENT: Execution Engine] - Implement tool functionality
    # First get the forecast grid endpoint
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)

    # [COMPONENT: Execution Engine] - Handle API failures gracefully
    if not points_data:
        return "Unable to fetch forecast data for this location."

    # Get the forecast URL from the points response
    forecast_url = points_data["properties"]["forecast"]
    forecast_data = await make_nws_request(forecast_url)

    # [COMPONENT: Execution Engine] - Handle API failures gracefully
    if not forecast_data:
        return "Unable to fetch detailed forecast."

    # Format the periods into a readable forecast
    periods = forecast_data["properties"]["periods"]
    forecasts = []
    for period in periods[:5]:  # Only show next 5 periods
        forecast = f"""
{period['name']}:
Temperature: {period['temperature']}°{period['temperatureUnit']}
Wind: {period['windSpeed']} {period['windDirection']}
Forecast: {period['detailedForecast']}
"""
        forecasts.append(forecast)

    return "\n---\n".join(forecasts)

# [COMPONENT: Transport] - Server lifecycle and transport configuration
if __name__ == "__main__":
    # [COMPONENT: Transport] - Configure and run server with stdio transport
    mcp.run(transport='stdio')