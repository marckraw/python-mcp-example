# Simple MCP Server Example

A simple Model Context Protocol (MCP) server built with Python, designed to be deployed on Railway.app or run locally. This server demonstrates the basic structure of an MCP server with support for both SSE (Server-Sent Events) and stdio modes.

## 🚀 Features

- **Multiple Transport Modes**: Supports both SSE (web) and stdio modes
- **Simple Tools**: Includes basic demonstration tools:
  - `get_current_time`: Returns the current date and time
  - `calculator`: Performs basic math operations (add, subtract, multiply, divide)
  - `echo`: Echoes back any message
- **Railway Ready**: Configured for easy deployment on Railway.app
- **Health Checks**: Built-in health check endpoint
- **Proper Error Handling**: Comprehensive error handling and logging

## 🛠️ Local Development Setup

### Prerequisites

- Python 3.10 or higher
- pip (Python package installer)

### Installation

1. **Clone and navigate to the project:**

   ```bash
   cd python-mcp-example
   ```

2. **Create and activate a virtual environment:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## 🏃 Running the Server

### SSE Mode (Web Server - Default)

This is the preferred mode for Railway deployment:

```bash
python main.py
```

The server will start on `http://localhost:8000` with the following endpoints:

- `/` - Server information and available tools
- `/health` - Health check endpoint
- `/sse` - SSE endpoint for MCP communication (not fully implemented in this example)

### Stdio Mode

For local testing with MCP clients that use stdio:

```bash
python main.py stdio
```

## 🌐 Railway Deployment

1. **Connect your GitHub repository to Railway**
2. **Railway will automatically detect the Python project and use the configuration from `railway.json`**
3. **The server will start automatically using the SSE mode**

### Environment Variables

Railway will automatically set the `PORT` environment variable. The server uses port 8000 by default locally.

## 🔧 API Usage Examples

### Using curl to test endpoints:

```bash
# Check server info
curl http://localhost:8000/

# Health check
curl http://localhost:8000/health
```

## 🏗️ Architecture

This MCP server demonstrates:

- **Server Registration**: Proper MCP server initialization
- **Tool Discovery**: Implementation of `list_tools` handler
- **Tool Execution**: Implementation of `call_tool` handler
- **Type Safety**: Using Pydantic models for request validation
- **Error Handling**: Comprehensive error handling with proper MCP responses
- **Dual Mode Support**: Both web (SSE) and stdio transport modes

## 📁 Project Structure

```
.
├── main.py           # Main server implementation
├── requirements.txt  # Python dependencies
├── railway.json      # Railway deployment config
├── Procfile         # Alternative deployment config
├── README.md        # This file
└── venv/           # Virtual environment (created locally)
```

## 🔍 Available Tools

### 1. get_current_time

- **Description**: Returns the current date and time
- **Arguments**: None
- **Example Response**: "Current time: 2024-12-27 16:35:22"

### 2. calculator

- **Description**: Performs basic mathematical operations
- **Arguments**:
  - `operation`: "add", "subtract", "multiply", or "divide"
  - `a`: First number
  - `b`: Second number
- **Example**: `{"operation": "add", "a": 5, "b": 3}` → "Result: 5 add 3 = 8"

### 3. echo

- **Description**: Echoes back the provided message
- **Arguments**:
  - `message`: String to echo back
- **Example**: `{"message": "Hello World"}` → "Echo: Hello World"

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you're in the virtual environment and all dependencies are installed
2. **Port Already in Use**: The default port 8000 might be busy, Railway will automatically assign a different port
3. **Module Not Found**: Ensure you're running the command from the project root directory

### Logs

The server includes comprehensive logging. Check the console output for detailed error messages and debugging information.

## 🚀 Next Steps

This is a basic example to get you started. To build more advanced MCP servers, consider:

- Adding more sophisticated tools
- Implementing proper SSE communication for MCP protocol
- Adding authentication and authorization
- Implementing resources and prompts features
- Adding persistent storage
- Creating more complex business logic

## 📚 Resources

- [Model Context Protocol Specification](https://modelcontextprotocol.io/specification/2025-03-26)
- [Python MCP SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Railway Deployment Docs](https://docs.railway.app/)

## 📝 License

This project is open source and available under the MIT License.
