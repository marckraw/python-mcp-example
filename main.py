#!/usr/bin/env python3
"""
Official MCP Server with SSE Support
Using the official Python SDK FastMCP
"""

import os
from datetime import datetime
from mcp.server.fastmcp import FastMCP

# Load environment variables from .env file (for local development)
try:
    from dotenv import load_dotenv
    load_dotenv()  # This loads .env file automatically
except ImportError:
    # dotenv not installed, skip (production might not need it)
    pass

# Create FastMCP server using official SDK
server_name = os.environ.get("SERVER_NAME", "Simple Example Server")
mcp = FastMCP(server_name)

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
    # Set environment variables for FastMCP (it uses these internally)
    port = int(os.environ.get("PORT", 12345))
    os.environ.setdefault("HOST", "0.0.0.0")  # Bind to all interfaces for Railway
    os.environ.setdefault("PORT", str(port))
    
    # Run with SSE transport - FastMCP handles host/port from environment
    mcp.run(transport="sse") 