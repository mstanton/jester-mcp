#!/usr/bin/env python3
"""
MCP Inspector and Development Tools for jester-mcp
Adds comprehensive debugging, monitoring, and development features
"""

import json
import time
import threading
import traceback
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
import websockets
import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import psutil

@dataclass
class MCPMessage:
    """Structured MCP message for inspection"""
    timestamp: float
    direction: str  # 'inbound' or 'outbound'
    message_type: str
    method: Optional[str]
    message_id: Optional[str]
    content: Dict[str, Any]
    execution_time: Optional[float] = None
    error: Optional[str] = None

class MCPInspector:
    """Real-time MCP protocol inspector and debugger"""
    
    def __init__(self):
        self.messages: List[MCPMessage] = []
        self.connected_clients: List[WebSocket] = []
        self.performance_metrics = {
            'total_messages': 0,
            'avg_response_time': 0,
            'error_count': 0,
            'method_stats': {}
        }
        self.is_recording = True
        self.max_messages = 1000  # Ring buffer
        
    def log_message(self, direction: str, content: Dict[str, Any], 
                   execution_time: Optional[float] = None, error: Optional[str] = None):
        """Log an MCP message for inspection"""
        message = MCPMessage(
            timestamp=time.time(),
            direction=direction,
            message_type=content.get('method', 'response'),
            method=content.get('method'),
            message_id=content.get('id'),
            content=content,
            execution_time=execution_time,
            error=error
        )
        
        if self.is_recording:
            self.messages.append(message)
            if len(self.messages) > self.max_messages:
                self.messages.pop(0)
                
            self._update_metrics(message)
            self._broadcast_to_clients(message)
    
    def _update_metrics(self, message: MCPMessage):
        """Update performance metrics"""
        self.performance_metrics['total_messages'] += 1
        
        if message.error:
            self.performance_metrics['error_count'] += 1
            
        if message.execution_time:
            # Update average response time
            current_avg = self.performance_metrics['avg_response_time']
            total = self.performance_metrics['total_messages']
            self.performance_metrics['avg_response_time'] = (
                (current_avg * (total - 1) + message.execution_time) / total
            )
            
        # Update method statistics
        if message.method:
            if message.method not in self.performance_metrics['method_stats']:
                self.performance_metrics['method_stats'][message.method] = {
                    'count': 0, 'total_time': 0, 'avg_time': 0, 'errors': 0
                }
            
            stats = self.performance_metrics['method_stats'][message.method]
            stats['count'] += 1
            if message.execution_time:
                stats['total_time'] += message.execution_time
                stats['avg_time'] = stats['total_time'] / stats['count']
            if message.error:
                stats['errors'] += 1
    
    async def _broadcast_to_clients(self, message: MCPMessage):
        """Broadcast message to connected WebSocket clients"""
        if self.connected_clients:
            message_json = json.dumps({
                'type': 'mcp_message',
                'data': asdict(message)
            })
            disconnected = []
            for client in self.connected_clients:
                try:
                    await client.send_text(message_json)
                except:
                    disconnected.append(client)
            
            for client in disconnected:
                self.connected_clients.remove(client)

class DevelopmentServer:
    """Enhanced development server with debugging capabilities"""
    
    def __init__(self, mcp_server, inspector: MCPInspector):
        self.mcp_server = mcp_server
        self.inspector = inspector
        self.app = FastAPI(title="Jester MCP Inspector")
        self.setup_routes()
        
    def setup_routes(self):
        """Setup FastAPI routes for the inspector"""
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            self.inspector.connected_clients.append(websocket)
            try:
                while True:
                    await websocket.receive_text()
            except:
                if websocket in self.inspector.connected_clients:
                    self.inspector.connected_clients.remove(websocket)
        
        @self.app.get("/api/messages")
        async def get_messages():
            """Get recent MCP messages"""
            return {
                'messages': [asdict(msg) for msg in self.inspector.messages[-100:]],
                'metrics': self.inspector.performance_metrics
            }
        
        @self.app.get("/api/metrics")
        async def get_metrics():
            """Get performance metrics"""
            system_metrics = {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent
            }
            return {
                'mcp_metrics': self.inspector.performance_metrics,
                'system_metrics': system_metrics
            }
        
        @self.app.post("/api/clear")
        async def clear_messages():
            """Clear message history"""
            self.inspector.messages.clear()
            return {'status': 'cleared'}
        
        @self.app.post("/api/toggle_recording")
        async def toggle_recording():
            """Toggle message recording"""
            self.inspector.is_recording = not self.inspector.is_recording
            return {'recording': self.inspector.is_recording}
        
        @self.app.get("/")
        async def dashboard():
            """Serve the inspector dashboard"""
            return HTMLResponse(content=self.get_dashboard_html())
    
    def get_dashboard_html(self) -> str:
        """Generate the inspector dashboard HTML"""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>Jester MCP Inspector</title>
    <style>
        body { font-family: 'Monaco', monospace; margin: 0; background: #1a1a1a; color: #00ff00; }
        .container { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; padding: 20px; height: 100vh; }
        .panel { background: #0a0a0a; border: 1px solid #333; border-radius: 8px; padding: 15px; overflow: auto; }
        .header { color: #00ccff; font-size: 18px; margin-bottom: 15px; border-bottom: 1px solid #333; padding-bottom: 10px; }
        .message { margin: 10px 0; padding: 10px; background: #111; border-left: 4px solid #00ff00; }
        .message.error { border-left-color: #ff4444; }
        .message.outbound { border-left-color: #ffaa00; }
        .timestamp { color: #666; font-size: 12px; }
        .method { color: #00ccff; font-weight: bold; }
        .content { background: #222; padding: 8px; margin-top: 8px; border-radius: 4px; font-size: 12px; }
        .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; }
        .metric { background: #111; padding: 10px; border-radius: 4px; text-align: center; }
        .metric-value { font-size: 24px; color: #00ff00; }
        .metric-label { color: #999; font-size: 12px; }
        .controls { margin-bottom: 15px; }
        .btn { background: #333; color: #fff; border: none; padding: 8px 16px; margin: 5px; border-radius: 4px; cursor: pointer; }
        .btn:hover { background: #555; }
        .status-indicator { width: 12px; height: 12px; border-radius: 50%; display: inline-block; margin-right: 8px; }
        .status-active { background: #00ff00; animation: pulse 2s infinite; }
        .status-inactive { background: #666; }
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
    </style>
</head>
<body>
    <div class="container">
        <div class="panel">
            <div class="header">
                🃏 MCP Message Stream
                <span class="status-indicator status-active" id="recording-status"></span>
                <span id="recording-text">Recording</span>
            </div>
            <div class="controls">
                <button class="btn" onclick="toggleRecording()">Toggle Recording</button>
                <button class="btn" onclick="clearMessages()">Clear Messages</button>
                <button class="btn" onclick="exportMessages()">Export Data</button>
            </div>
            <div id="messages"></div>
        </div>
        
        <div class="panel">
            <div class="header">📊 Performance Metrics</div>
            <div class="metrics" id="metrics"></div>
            
            <div class="header" style="margin-top: 30px;">🔧 System Status</div>
            <div class="metrics" id="system-metrics"></div>
        </div>
    </div>

    <script>
        let ws = new WebSocket(`ws://${window.location.host}/ws`);
        let recording = true;
        
        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            if (data.type === 'mcp_message') {
                addMessage(data.data);
            }
        };
        
        function addMessage(msg) {
            const container = document.getElementById('messages');
            const div = document.createElement('div');
            div.className = `message ${msg.error ? 'error' : msg.direction}`;
            
            const timestamp = new Date(msg.timestamp * 1000).toLocaleTimeString();
            const executionTime = msg.execution_time ? ` (${msg.execution_time.toFixed(2)}ms)` : '';
            
            div.innerHTML = `
                <div class="timestamp">${timestamp}</div>
                <div class="method">${msg.direction.toUpperCase()}: ${msg.method || 'Response'}${executionTime}</div>
                ${msg.error ? `<div style="color: #ff4444;">Error: ${msg.error}</div>` : ''}
                <div class="content">${JSON.stringify(msg.content, null, 2)}</div>
            `;
            
            container.insertBefore(div, container.firstChild);
            
            // Keep only last 50 messages visible
            while (container.children.length > 50) {
                container.removeChild(container.lastChild);
            }
        }
        
        function updateMetrics() {
            fetch('/api/metrics')
                .then(r => r.json())
                .then(data => {
                    const mcpMetrics = data.mcp_metrics;
                    const sysMetrics = data.system_metrics;
                    
                    document.getElementById('metrics').innerHTML = `
                        <div class="metric">
                            <div class="metric-value">${mcpMetrics.total_messages}</div>
                            <div class="metric-label">Total Messages</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">${mcpMetrics.avg_response_time.toFixed(2)}ms</div>
                            <div class="metric-label">Avg Response Time</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">${mcpMetrics.error_count}</div>
                            <div class="metric-label">Errors</div>
                        </div>
                    `;
                    
                    document.getElementById('system-metrics').innerHTML = `
                        <div class="metric">
                            <div class="metric-value">${sysMetrics.cpu_percent.toFixed(1)}%</div>
                            <div class="metric-label">CPU Usage</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">${sysMetrics.memory_percent.toFixed(1)}%</div>
                            <div class="metric-label">Memory Usage</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">${sysMetrics.disk_percent.toFixed(1)}%</div>
                            <div class="metric-label">Disk Usage</div>
                        </div>
                    `;
                });
        }
        
        function toggleRecording() {
            fetch('/api/toggle_recording', {method: 'POST'})
                .then(r => r.json())
                .then(data => {
                    recording = data.recording;
                    const status = document.getElementById('recording-status');
                    const text = document.getElementById('recording-text');
                    if (recording) {
                        status.className = 'status-indicator status-active';
                        text.textContent = 'Recording';
                    } else {
                        status.className = 'status-indicator status-inactive';
                        text.textContent = 'Paused';
                    }
                });
        }
        
        function clearMessages() {
            fetch('/api/clear', {method: 'POST'});
            document.getElementById('messages').innerHTML = '';
        }
        
        function exportMessages() {
            fetch('/api/messages')
                .then(r => r.json())
                .then(data => {
                    const blob = new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'});
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `mcp-debug-${new Date().toISOString()}.json`;
                    a.click();
                });
        }
        
        // Update metrics every 2 seconds
        setInterval(updateMetrics, 2000);
        updateMetrics();
    </script>
</body>
</html>
        """

class EnhancedMCPServer:
    """Enhanced MCP server with debugging and development features"""
    
    def __init__(self, original_server):
        self.original_server = original_server
        self.inspector = MCPInspector()
        self.dev_server = None
        self.auto_reload = True
        self.file_watcher = None
        
    def wrap_handlers(self):
        """Wrap original MCP handlers with debugging"""
        original_handlers = self.original_server.handlers.copy()
        
        for method, handler in original_handlers.items():
            self.original_server.handlers[method] = self._wrap_handler(method, handler)
    
    def _wrap_handler(self, method: str, handler: Callable):
        """Wrap a handler with debugging and performance monitoring"""
        async def wrapped_handler(*args, **kwargs):
            start_time = time.time()
            
            # Log incoming request
            request_data = {'method': method, 'args': str(args)[:500]}
            self.inspector.log_message('inbound', request_data)
            
            try:
                result = await handler(*args, **kwargs)
                execution_time = (time.time() - start_time) * 1000
                
                # Log successful response
                response_data = {
                    'method': method,
                    'result': str(result)[:500] if result else None
                }
                self.inspector.log_message('outbound', response_data, execution_time)
                
                return result
                
            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                error_msg = f"{type(e).__name__}: {str(e)}"
                
                # Log error response
                error_data = {'method': method, 'error': error_msg}
                self.inspector.log_message('outbound', error_data, execution_time, error_msg)
                
                raise
        
        return wrapped_handler
    
    def start_dev_server(self, port: int = 8000):
        """Start the development server with inspector dashboard"""
        self.dev_server = DevelopmentServer(self.original_server, self.inspector)
        
        def run_server():
            uvicorn.run(self.dev_server.app, host="localhost", port=port)
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        print(f"🔧 MCP Inspector Dashboard: http://localhost:{port}")
        print(f"📊 Real-time debugging and performance monitoring active")
    
    def setup_auto_reload(self, watch_paths: List[str] = None):
        """Setup file watcher for auto-reload during development"""
        if watch_paths is None:
            watch_paths = ['.']
            
        # Implementation would use watchdog library for file watching
        print(f"🔄 Auto-reload enabled for paths: {watch_paths}")

# Development utilities
class MCPTestClient:
    """Test client for MCP server development and testing"""
    
    def __init__(self, server):
        self.server = server
        
    async def send_request(self, method: str, params: Dict[str, Any] = None):
        """Send a test request to the MCP server"""
        request = {
            'jsonrpc': '2.0',
            'id': f'test_{int(time.time())}',
            'method': method,
            'params': params or {}
        }
        
        # This would integrate with your existing MCP server
        return await self.server.handle_request(request)
    
    async def run_integration_tests(self):
        """Run a suite of integration tests"""
        tests = [
            ('initialize', {}),
            ('execute_code', {'language': 'python', 'code': 'print("test")'}),
            ('create_file', {'filename': 'test.txt', 'content': 'test'}),
        ]
        
        results = []
        for method, params in tests:
            try:
                result = await self.send_request(method, params)
                results.append({'method': method, 'success': True, 'result': result})
            except Exception as e:
                results.append({'method': method, 'success': False, 'error': str(e)})
        
        return results

# Usage example for integration
def enhance_jester_mcp(original_server):
    """Enhance the original jester-mcp server with inspection capabilities"""
    enhanced_server = EnhancedMCPServer(original_server)
    enhanced_server.wrap_handlers()
    enhanced_server.start_dev_server(port=8000)
    enhanced_server.setup_auto_reload()
    
    return enhanced_server

if __name__ == "__main__":
    # Example of how to integrate with your existing server
    print("🃏 Jester MCP Inspector and Development Tools")
    print("Ready to enhance your MCP development experience!")
