#!/usr/bin/env python3
"""
MCP Server with SSE Support using FastMCP
This is the recommended approach for SSE-based MCP servers
"""

import os
import asyncio
import logging
from datetime import datetime
from typing import Any

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastMCP server
mcp = FastMCP("Simple Example Server")


class CalculatorArgs(BaseModel):
    """Arguments for calculator tool"""
    operation: str
    a: float
    b: float


class EchoArgs(BaseModel):
    """Arguments for echo tool"""
    message: str


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


# Add some resources for demonstration
@mcp.resource("time://current")
def current_time_resource() -> str:
    """Resource that provides current time"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")


@mcp.resource("server://info")
def server_info_resource() -> str:
    """Resource that provides server information"""
    return "Simple MCP Server with Calculator, Echo, and Time tools"


if __name__ == "__main__":
    # Set environment variables for FastMCP
    port = int(os.environ.get("PORT", 8000))
    os.environ.setdefault("HOST", "0.0.0.0")
    os.environ.setdefault("PORT", str(port))
    
    logger.info(f"Starting FastMCP server with SSE transport on port {port}")
    
    # Run with SSE transport
    mcp.run(transport="sse") 