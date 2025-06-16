#!/usr/bin/env python3
"""
Simple MCP Server Example
Supports both SSE (Server-Sent Events) and stdio modes
Priority: SSE for web deployment on Railway.app
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    TextContent,
    Tool,
)
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create MCP server instance
server = Server("simple-example-server")

# FastAPI app for SSE endpoint
app = FastAPI(title="Simple MCP Server", version="1.0.0")


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


@app.get("/")
async def root():
    """Root endpoint with server info"""
    return {
        "name": "Simple MCP Server",
        "version": "1.0.0",
        "description": "A simple MCP server example with basic tools",
        "endpoints": {
            "sse": "/sse",
            "health": "/health"
        },
        "tools": ["get_current_time", "calculator", "echo"]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/sse")
async def sse_endpoint(request: Request):
    """Server-Sent Events endpoint for MCP communication"""
    
    # CORS headers
    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    }
    
    async def event_generator():
        try:
            # Create SSE transport and connect
            from mcp.server.sse import SseServerTransport
            
            # Initialize transport
            transport = SseServerTransport("/message")
            
            # Handle the request body for initialization
            body = await request.body()
            if body:
                # Process any initialization data
                logger.info(f"Received initialization data: {body.decode()[:100]}...")
            
            # Start the MCP server session
            async with transport.connect_sse(request) as streams:
                read_stream, write_stream = streams
                
                # Run the MCP server
                await server.run(
                    read_stream, 
                    write_stream, 
                    server.create_initialization_options()
                )
                
        except Exception as e:
            logger.error(f"SSE connection error: {e}")
            # Send error event
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers=headers,
    )


@app.options("/sse")
async def sse_options():
    """Handle CORS preflight requests for SSE endpoint"""
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    }
    return {"message": "OK"}, headers


@app.get("/message")
async def message_endpoint():
    """Message endpoint for SSE transport"""
    return {"status": "ready"}


@app.post("/message")
async def message_post_endpoint(request: Request):
    """Handle POST messages for SSE transport"""
    body = await request.body()
    logger.info(f"Received message: {body.decode()[:200]}...")
    return {"status": "received"}


async def run_stdio():
    """Run the server in stdio mode"""
    logger.info("Starting MCP server in stdio mode")
    
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, write_stream, server.create_initialization_options()
        )


def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == "stdio":
        # Run in stdio mode
        asyncio.run(run_stdio())
    else:
        # Run in SSE mode (default for Railway deployment)
        port = int(os.environ.get("PORT", 8000))
        logger.info(f"Starting MCP server in SSE mode on port {port}")
        uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main() 