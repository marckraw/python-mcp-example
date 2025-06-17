#!/usr/bin/env python3
"""
Official MCP Server with SSE Support
Using the official Python SDK FastMCP
"""

import os
from datetime import datetime
from mcp.server.fastmcp import FastMCP
from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer

# Load environment variables from .env file (for local development)
try:
    from dotenv import load_dotenv
    load_dotenv()  # This loads .env file automatically
except ImportError:
    # dotenv not installed, skip (production might not need it)
    pass

# Simple API key authentication
def verify_api_key(request: Request) -> bool:
    """Verify API key from request headers"""
    api_key = os.environ.get("API_KEY")
    
    # If no API key is configured, skip authentication
    if not api_key:
        return True
    
    # Check Authorization header: "Bearer your-api-key"
    auth_header = request.headers.get("authorization", "")
    if auth_header.startswith("Bearer "):
        provided_key = auth_header[7:]  # Remove "Bearer " prefix
        if provided_key == api_key:
            return True
    
    # Check X-API-Key header (alternative)
    api_key_header = request.headers.get("x-api-key", "")
    if api_key_header == api_key:
        return True
    
    # Authentication failed
    raise HTTPException(
        status_code=401, 
        detail="Invalid or missing API key. Use 'Authorization: Bearer your-api-key' or 'X-API-Key: your-api-key' header."
    )

# Create FastMCP server
server_name = os.environ.get("SERVER_NAME", "Simple Example Server")
mcp = FastMCP(server_name)

# Show auth status
api_key = os.environ.get("API_KEY")
if api_key and api_key != "your-secret-api-key-here":
    print(f"🔒 API key authentication configured")
else:
    print(f"⚠️  No API key set - authentication disabled")

# Authentication middleware that will be applied to the FastAPI app
async def auth_middleware(request: Request, call_next):
    """Simple API key authentication middleware"""
    # Skip auth for health checks and static files
    if request.url.path in ["/health", "/", "/docs", "/openapi.json"]:
        response = await call_next(request)
        return response
    
    # Verify API key
    verify_api_key(request)
    
    # Continue with request
    response = await call_next(request)
    return response

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
    
    # Add authentication middleware if API key is configured
    api_key = os.environ.get("API_KEY")
    if api_key:
        # Get the FastAPI app and add middleware
        app = mcp.sse_app()
        app.middleware("http")(auth_middleware)
        print(f"🔒 API key authentication enabled")
        
        # Run the app directly with uvicorn
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=port)
    else:
        print(f"⚠️  No API key set - authentication disabled")
        # Run with SSE transport - FastMCP handles host/port from environment
        mcp.run(transport="sse") 