# Claude-Jester Enhanced MCP Server - Technical Documentation

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Installation & Setup](#installation--setup)
4. [Core Components](#core-components)
5. [API Reference](#api-reference)
6. [Security Framework](#security-framework)
7. [Performance Characteristics](#performance-characteristics)
8. [Usage Examples](#usage-examples)
9. [Configuration](#configuration)
10. [Troubleshooting](#troubleshooting)
11. [Development](#development)

---

## Overview

The Claude-Jester Enhanced MCP Server is a Model Context Protocol implementation that provides secure code execution capabilities for AI assistants. It combines traditional subprocess execution with enterprise-grade containerization using Podman, advanced slash command processing, and quantum debugging features.

### Key Features

- **Multi-level Security**: Subprocess, container isolation, and development modes
- **Podman Integration**: Rootless containerization with resource limits
- **Slash Commands**: Extensible command system for advanced operations
- **Quantum Debugging**: Parallel algorithm testing and optimization
- **Language Support**: Python, JavaScript, Bash with extensible architecture
- **Performance Monitoring**: Execution time, memory usage, and resource tracking

### Technical Specifications

- **Protocol**: MCP (Model Context Protocol) 2024-11-05
- **Language**: Python 3.7+
- **Dependencies**: Podman (optional), Node.js (for JavaScript execution)
- **Container Runtime**: Podman with rootless configuration
- **Logging**: Comprehensive stderr logging with configurable levels

---

## Architecture

### High-Level Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Claude Desktop                           │
└─────────────────────┬───────────────────────────────────────┘
                      │ MCP Protocol (JSON-RPC)
┌─────────────────────▼───────────────────────────────────────┐
│                Enhanced MCP Server                          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │ Slash Commands  │  │ Code Execution  │  │    Podman    │ │
│  │    System       │  │    Engine       │  │  Integration │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Component Details

#### 1. EnhancedMCPServer
- **Purpose**: Main server class handling MCP protocol communication
- **Responsibilities**: Request routing, response formatting, error handling
- **Methods**: `handle_initialize()`, `handle_list_tools()`, `handle_call_tool()`

#### 2. PodmanCodeExecutor
- **Purpose**: Container-based code execution with multiple security levels
- **Security Modes**: isolation, persistent, development
- **Features**: Resource limits, network isolation, filesystem restrictions

#### 3. IntegratedSlashCommands
- **Purpose**: Command processing system for advanced operations
- **Commands**: 15+ built-in commands across 8 categories
- **Extensibility**: Plugin architecture for custom commands

---

## Installation & Setup

### Prerequisites

```bash
# Required
python >= 3.7
Claude Desktop application

# Optional (for container features)
podman >= 3.0
nodejs >= 14.0 (for JavaScript execution)
```

### Installation Steps

1. **Download the Server**
   ```bash
   # Save standalone_mcp_server.py to your desired location
   curl -O https://path/to/standalone_mcp_server.py
   chmod +x standalone_mcp_server.py
   ```

2. **Configure Claude Desktop**
   
   Edit your Claude Desktop configuration file:
   
   **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   
   ```json
   {
     "mcpServers": {
       "claude-jester": {
         "command": "python",
         "args": ["/absolute/path/to/standalone_mcp_server.py"],
         "env": {
           "PYTHONPATH": "/path/to/execution/environment"
         }
       }
     }
   }
   ```

3. **Verify Installation**
   ```bash
   # Test server directly
   echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | python standalone_mcp_server.py
   ```

### Optional: Podman Setup

```bash
# Install Podman (varies by OS)
# Ubuntu/Debian
sudo apt-get install podman

# macOS
brew install podman

# Initialize rootless Podman
podman system reset --force
```

---

## Core Components

### 1. ExecutionResult Data Structure

```python
@dataclass
class ExecutionResult:
    success: bool                    # Execution success status
    output: str                      # Standard output
    error: str                       # Error messages
    execution_time: float            # Execution time in seconds
    memory_usage: int                # Memory usage in MB
    container_id: Optional[str]      # Container identifier (if used)
    security_level: str              # Security level applied
    method: str                      # Execution method used
```

### 2. Security Levels

#### Isolation Mode
- **Container**: Ephemeral, removed after execution
- **Network**: Completely disabled
- **Filesystem**: Read-only with limited tmp space
- **User**: nobody (non-root)
- **Resources**: 128MB memory, 0.5 CPU cores
- **Use Case**: Maximum security for untrusted code

#### Persistent Mode
- **Container**: Reusable session containers
- **Network**: Disabled
- **Filesystem**: Read-only with writable tmp
- **User**: nobody
- **Resources**: 128MB memory, 0.5 CPU cores
- **Use Case**: Performance optimization for multiple executions

#### Development Mode
- **Container**: Ephemeral with relaxed restrictions
- **Network**: Limited (slirp4netns)
- **Filesystem**: Writable tmp, larger space
- **User**: developer
- **Resources**: 512MB memory, 1.0 CPU cores
- **Use Case**: Development and debugging

### 3. Fallback Execution

When Podman is unavailable, the server falls back to subprocess execution:

```python
# Fallback characteristics
- Timeout: 30 seconds
- Working Directory: Temporary directory
- Resource Limits: OS-level only
- Security: Process isolation only
```

---

## API Reference

### MCP Protocol Implementation

The server implements the Model Context Protocol with the following endpoints:

#### Initialize
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {}
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "tools": {}
    },
    "serverInfo": {
      "name": "claude-jester-podman",
      "version": "3.0.0"
    }
  }
}
```

#### List Tools
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list",
  "params": {}
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "tools": [
      {
        "name": "execute_code",
        "description": "Execute code with quantum debugging, slash commands, and Podman containerization support",
        "inputSchema": {
          "type": "object",
          "properties": {
            "language": {
              "type": "string",
              "enum": ["python", "javascript", "bash", "slash"]
            },
            "code": {
              "type": "string"
            }
          },
          "required": ["language", "code"]
        }
      },
      {
        "name": "create_file",
        "description": "Create a file with specified content",
        "inputSchema": {
          "type": "object",
          "properties": {
            "filename": {"type": "string"},
            "content": {"type": "string"}
          },
          "required": ["filename", "content"]
        }
      }
    ]
  }
}
```

#### Execute Code
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "execute_code",
    "arguments": {
      "language": "python",
      "code": "print('Hello World!')"
    }
  }
}
```

### Slash Commands API

The server supports an extensive slash command system accessible via the `execute_code` tool with `language: "slash"`.

#### Core Commands

| Command | Category | Description | Usage |
|---------|----------|-------------|--------|
| `/help` | System | Show available commands | `/help [command]` |
| `/status` | System | System status information | `/status [component]` |
| `/run` | Execution | Execute code with debugging | `/run <lang> <code>` |
| `/container` | Podman | Container execution | `/container <level> <lang> <code>` |
| `/quantum` | Quantum | Algorithm optimization | `/quantum <task>` |
| `/benchmark` | Performance | Performance testing | `/benchmark <lang> <code> [iter]` |
| `/secure_run` | Security | Maximum security execution | `/secure_run <lang> <code>` |
| `/cleanup` | System | Container cleanup | `/cleanup [session_id]` |

#### Advanced Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/quantum_container` | Quantum debugging in containers | `/quantum_container sort algorithms` |
| `/dev_run` | Development-friendly execution | `/dev_run python import requests` |
| `/podman_status` | Podman system information | `/podman_status containers` |

---

## Security Framework

### Multi-Layer Defense

1. **Input Validation**
   - JSON-RPC parameter validation
   - Path traversal prevention for file operations
   - Command injection protection

2. **Execution Isolation**
   - **Level 1**: Process isolation (subprocess)
   - **Level 2**: Container isolation (Podman)
   - **Level 3**: User namespace separation
   - **Level 4**: Network isolation

3. **Resource Controls**
   ```python
   # Default resource limits
   MEMORY_LIMIT = "128m"
   CPU_LIMIT = "0.5"
   TIMEOUT = 30  # seconds
   TMP_SIZE = "64m"
   ```

4. **Container Security Features**
   - Read-only root filesystem
   - Dropped capabilities (`--cap-drop ALL`)
   - No new privileges (`--security-opt no-new-privileges`)
   - Non-root user execution (`--user nobody`)
   - Network isolation (`--network none`)

### Security Analysis

The integrated security analyzer detects potentially dangerous code patterns:

```python
dangerous_patterns = [
    ("import os", "File system access"),
    ("subprocess", "System command execution"),
    ("exec(", "Code injection risk"),
    ("eval(", "Expression evaluation risk"),
    ("open(", "File access"),
    ("urllib", "Network access"),
    ("socket", "Network socket access"),
    # ... additional patterns
]
```

---

## Performance Characteristics

### Execution Time Benchmarks

| Execution Mode | Startup Time | Overhead | Memory Usage |
|----------------|--------------|----------|--------------|
| Subprocess | 45ms | 5% | 15MB baseline |
| Container (Isolation) | 180ms | 15% | 35MB baseline |
| Container (Persistent) | 65ms* | 5% | 45MB baseline |
| Container (Development) | 100ms | 10% | 50MB baseline |

*After initial container creation

### Resource Usage

```python
# Memory allocation per execution
CONTAINER_OVERHEAD = 20-30MB
PYTHON_INTERPRETER = 10-15MB
CODE_EXECUTION = Variable
TOTAL_MEMORY = 35-75MB per execution

# CPU utilization
CONTAINER_STARTUP = 0.1-0.3 CPU seconds
CODE_EXECUTION = Variable
CLEANUP = 0.05-0.1 CPU seconds
```

### Scalability Metrics

- **Concurrent Executions**: Limited by system resources
- **Container Lifecycle**: <200ms startup time
- **Session Containers**: Up to 10 simultaneous sessions
- **Memory Efficiency**: Shared base images reduce overhead

---

## Usage Examples

### Basic Code Execution

```python
# Python execution
{
  "language": "python",
  "code": "print('Hello World!')"
}

# JavaScript execution
{
  "language": "javascript", 
  "code": "console.log('Hello World!');"
}

# Bash execution
{
  "language": "bash",
  "code": "echo 'Hello World!'"
}
```

### Container Execution

```python
# Maximum security
{
  "language": "slash",
  "code": "/container isolation python print('Secure execution')"
}

# Session container
{
  "language": "slash", 
  "code": "/container persistent python import math; print(math.pi)"
}

# Development mode
{
  "language": "slash",
  "code": "/dev_run python import requests; print('Network enabled')"
}
```

### Quantum Debugging

```python
# Algorithm optimization
{
  "language": "slash",
  "code": "/quantum find fastest sorting algorithm"
}

# Performance comparison
{
  "language": "slash",
  "code": "/benchmark python sum(i*i for i in range(1000)) 50"
}
```

### System Management

```python
# System status
{
  "language": "slash",
  "code": "/status"
}

# Container cleanup
{
  "language": "slash", 
  "code": "/cleanup"
}

# Podman information
{
  "language": "slash",
  "code": "/podman_status"
}
```

---

## Configuration

### Environment Variables

```bash
# Optional configuration
PYTHONPATH=/path/to/execution/environment
LOG_LEVEL=DEBUG|INFO|WARNING|ERROR
MCP_TIMEOUT=30
MCP_MEMORY_LIMIT=128m
```

### Server Configuration

```python
# PodmanCodeExecutor configuration
config = {
    "timeout": 30,              # Execution timeout (seconds)
    "memory_limit": "128m",     # Memory limit for containers
    "cpu_limit": "0.5",         # CPU limit (cores)
    "network": "none",          # Network configuration
    "read_only": True,          # Read-only filesystem
    "tmp_size": "64m",          # Temporary space size
    "max_containers": 10        # Maximum concurrent containers
}
```

### Base Images

```python
base_images = {
    "python": "docker.io/python:3.11-alpine",
    "javascript": "docker.io/node:18-alpine",
    "bash": "docker.io/alpine:latest",
    "rust": "docker.io/rust:1.70-alpine",
    "go": "docker.io/golang:1.20-alpine"
}
```

---

## Troubleshooting

### Common Issues

#### 1. MCP Server Won't Start

**Symptoms**: Claude Desktop shows connection errors

**Diagnosis**:
```bash
# Test server directly
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | python standalone_mcp_server.py
```

**Solutions**:
- Verify Python path in Claude Desktop config
- Check file permissions (`chmod +x standalone_mcp_server.py`)
- Ensure no syntax errors in configuration JSON

#### 2. Podman Execution Fails

**Symptoms**: Commands work but container execution fails

**Diagnosis**:
```bash
# Check Podman availability
podman --version
podman system info

# Test basic container
podman run --rm alpine echo "test"
```

**Solutions**:
- Install Podman if missing
- Initialize rootless Podman: `podman system reset`
- Check container image availability

#### 3. Permission Errors

**Symptoms**: File creation or execution permission denied

**Solutions**:
- Ensure write permissions in working directory
- Check if running in restricted environment
- Verify user has Podman access (rootless)

#### 4. Timeout Issues

**Symptoms**: Code execution times out frequently

**Configuration**:
```python
# Increase timeout in server configuration
"timeout": 60  # Increase from default 30 seconds
```

### Debug Mode

Enable detailed logging:

```bash
# Set environment variable
export LOG_LEVEL=DEBUG

# Or modify the logging configuration in the server
logging.basicConfig(level=logging.DEBUG)
```

### Performance Issues

#### Container Startup Latency

**Problem**: Slow container startup affecting performance

**Solutions**:
1. Use persistent containers for repeated executions
2. Pre-pull base images: `podman pull python:3.11-alpine`
3. Enable container caching

#### Memory Usage

**Problem**: High memory consumption

**Monitoring**:
```bash
# Monitor container resource usage
podman stats

# System resource monitoring
top -p $(pgrep -f standalone_mcp_server)
```

**Optimization**:
```python
# Adjust memory limits
"memory_limit": "64m"  # Reduce from default 128m
"max_containers": 5    # Reduce concurrent containers
```

---

## Development

### Extending the Server

#### Adding New Languages

```python
# In PodmanCodeExecutor._initialize_base_images()
def _initialize_base_images(self) -> Dict[str, str]:
    return {
        # ... existing languages
        "ruby": "docker.io/ruby:3.1-alpine",
        "php": "docker.io/php:8.1-alpine"
    }

# In _get_execution_command()
def _get_execution_command(self, language: str, file_path: str) -> List[str]:
    commands = {
        # ... existing commands
        "ruby": ["ruby", file_path],
        "php": ["php", file_path]
    }
    return commands.get(language, ["cat", file_path])
```

#### Custom Slash Commands

```python
# Add to IntegratedSlashCommands._register_commands()
SlashCommand(
    name="custom_command",
    description="Custom functionality",
    category=CommandCategory.EXECUTION,
    usage="/custom_command <args>",
    examples=["/custom_command example"],
    handler=self._handle_custom_command,
    aliases=["cc"]
)

# Implement handler
async def _handle_custom_command(self, args: List[str], full_command: str) -> str:
    # Custom implementation
    return "Custom command result"
```

#### Security Policy Customization

```python
# Custom security profiles
CUSTOM_SECURITY_PROFILE = {
    "memory_limit": "256m",
    "cpu_limit": "1.0",
    "network": "slirp4netns",  # Allow limited network
    "additional_caps": [],     # Custom capabilities
    "volume_mounts": []        # Custom volume mounts
}
```

### Testing

#### Unit Tests

```python
import asyncio
import pytest
from standalone_mcp_server import EnhancedMCPServer, PodmanCodeExecutor

@pytest.mark.asyncio
async def test_python_execution():
    executor = PodmanCodeExecutor()
    result = await executor.execute_code("print('test')", "python", "isolation")
    assert result.success
    assert "test" in result.output

@pytest.mark.asyncio 
async def test_slash_commands():
    server = EnhancedMCPServer()
    result = await server.slash_commands.process_command("/help")
    assert "Claude-Jester" in result
```

#### Integration Tests

```bash
# Test MCP protocol
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"execute_code","arguments":{"language":"python","code":"print(\"test\")"}}}' | python standalone_mcp_server.py

# Test container execution
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"execute_code","arguments":{"language":"slash","code":"/container isolation python print(\"container test\")"}}}' | python standalone_mcp_server.py
```

### Performance Monitoring

```python
# Add performance metrics
import time
import psutil

class PerformanceMonitor:
    def __init__(self):
        self.metrics = {
            "total_executions": 0,
            "total_time": 0,
            "average_time": 0,
            "memory_peak": 0
        }
    
    def record_execution(self, execution_time: float, memory_usage: int):
        self.metrics["total_executions"] += 1
        self.metrics["total_time"] += execution_time
        self.metrics["average_time"] = self.metrics["total_time"] / self.metrics["total_executions"]
        self.metrics["memory_peak"] = max(self.metrics["memory_peak"], memory_usage)
```

---

## Conclusion

The Claude-Jester Enhanced MCP Server provides a comprehensive solution for secure AI code execution, combining traditional subprocess execution with enterprise-grade containerization, advanced command processing, and performance optimization features. Its modular architecture allows for easy extension and customization while maintaining security and performance standards.

For additional information, issues, or contributions, refer to the project repository and documentation updates.

**Version**: 3.0.0  
**Last Updated**: December 2024  
**Protocol**: MCP 2024-11-05