#!/usr/bin/env python3
"""
Simple MCP Server - Stdio Version
Works with MCP Inspector and other MCP clients via stdio transport
"""

import asyncio
import logging
from datetime import datetime
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    TextContent,
    Tool,
)
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create MCP server instance
server = Server("simple-example-server")


class CalculatorArgs(BaseModel):
    """Arguments for calculator tool"""
    operation: str
    a: float
    b: float


class EchoArgs(BaseModel):
    """Arguments for echo tool"""
    message: str


@server.list_tools()
async def handle_list_tools() -> ListToolsResult:
    """List available tools"""
    return ListToolsResult(
        tools=[
            Tool(
                name="get_current_time",
                description="Get the current date and time",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            ),
            Tool(
                name="calculator",
                description="Perform basic mathematical operations (add, subtract, multiply, divide)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "enum": ["add", "subtract", "multiply", "divide"],
                            "description": "The mathematical operation to perform",
                        },
                        "a": {
                            "type": "number",
                            "description": "First number",
                        },
                        "b": {
                            "type": "number",
                            "description": "Second number",
                        },
                    },
                    "required": ["operation", "a", "b"],
                },
            ),
            Tool(
                name="echo",
                description="Echo back the provided message",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "Message to echo back",
                        },
                    },
                    "required": ["message"],
                },
            ),
        ]
    )


@server.call_tool()
async def handle_call_tool(request: CallToolRequest) -> CallToolResult:
    """Handle tool execution requests"""
    try:
        if request.name == "get_current_time":
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Current time: {current_time}")]
            )
        
        elif request.name == "calculator":
            args = CalculatorArgs(**request.arguments)
            
            if args.operation == "add":
                result = args.a + args.b
            elif args.operation == "subtract":
                result = args.a - args.b
            elif args.operation == "multiply":
                result = args.a * args.b
            elif args.operation == "divide":
                if args.b == 0:
                    return CallToolResult(
                        content=[TextContent(type="text", text="Error: Division by zero is not allowed")]
                    )
                result = args.a / args.b
            else:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: Unknown operation '{args.operation}'")]
                )
            
            return CallToolResult(
                content=[TextContent(type="text", text=f"Result: {args.a} {args.operation} {args.b} = {result}")]
            )
        
        elif request.name == "echo":
            args = EchoArgs(**request.arguments)
            return CallToolResult(
                content=[TextContent(type="text", text=f"Echo: {args.message}")]
            )
        
        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error: Unknown tool '{request.name}'")]
            )
    
    except Exception as e:
        logger.error(f"Error executing tool {request.name}: {e}")
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: {str(e)}")]
        )


async def main():
    """Main entry point for stdio server"""
    logger.info("Starting MCP server with stdio transport")
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, write_stream, server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main()) 