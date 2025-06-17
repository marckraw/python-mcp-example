#!/usr/bin/env python3
"""
Official MCP Server with SSE Support
Using the official Python SDK FastMCP
"""

import os
from datetime import datetime
from mcp.server.fastmcp import FastMCP

# Create FastMCP server using official SDK
mcp = FastMCP("Simple Example Server")

# Add tools using the official SDK decorators
@mcp.tool()
def get_current_time() -> str:
    """Get the current date and time"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"Current time: {current_time}"

@mcp.tool()
def calculator(operation: str, a: float, b: float) -> str:
    """Perform basic mathematical operations (add, subtract, multiply, divide)"""
    try:
        if operation == "add":
            result = a + b
        elif operation == "subtract":
            result = a - b
        elif operation == "multiply":
            result = a * b
        elif operation == "divide":
            if b == 0:
                return "Error: Division by zero is not allowed"
            result = a / b
        else:
            return f"Error: Unknown operation '{operation}'"
        
        return f"Result: {a} {operation} {b} = {result}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def echo(message: str) -> str:
    """Echo back the provided message"""
    return f"Echo: {message}"

# Add resources using the official SDK
@mcp.resource("time://current")
def current_time_resource() -> str:
    """Resource that provides current time"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")

@mcp.resource("server://info")
def server_info_resource() -> str:
    """Resource that provides server information"""
    return "Simple MCP Server with Calculator, Echo, and Time tools"

if __name__ == "__main__":
    # Get port from Railway environment variable
    port = int(os.environ.get("PORT", 8000))
    
    # Run with SSE transport for Railway deployment
    mcp.run(
        transport="sse",
        host="0.0.0.0",  # Important: bind to all interfaces for Railway
        port=port
    ) 