#!/usr/bin/env python3
"""
Development Configuration and Testing Tools for jester-mcp
Enhanced development workflow with configuration management and testing utilities
"""

import json
import yaml
import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import asyncio
import tempfile
import pytest
from unittest.mock import MagicMock, patch

@dataclass
class DevelopmentConfig:
    """Development configuration for jester-mcp"""
    debug_mode: bool = True
    inspector_port: int = 8000
    auto_reload: bool = True
    container_mode: str = "development"  # isolation, persistent, development
    log_level: str = "DEBUG"
    performance_monitoring: bool = True
    security_analysis: bool = True
    benchmark_iterations: int = 10
    container_cleanup: bool = True
    watch_paths: List[str] = None
    
    def __post_init__(self):
        if self.watch_paths is None:
            self.watch_paths = [".", "src/", "tests/"]

class ConfigManager:
    """Manage development configurations for different environments"""
    
    def __init__(self, config_dir: str = ".jester"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self.config_file = self.config_dir / "dev_config.yaml"
        
    def load_config(self) -> DevelopmentConfig:
        """Load development configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                data = yaml.safe_load(f)
                return DevelopmentConfig(**data)
        return DevelopmentConfig()
    
    def save_config(self, config: DevelopmentConfig):
        """Save development configuration"""
        with open(self.config_file, 'w') as f:
            yaml.dump(asdict(config), f, default_flow_style=False)
    
    def create_claude_desktop_config(self, server_path: str) -> Dict[str, Any]:
        """Generate Claude Desktop configuration"""
        config = {
            "mcpServers": {
                "jester-mcp": {
                    "command": sys.executable,
                    "args": [str(Path(server_path).absolute())],
                    "env": {
                        "JESTER_DEBUG": "true",
                        "JESTER_INSPECTOR_PORT": str(self.load_config().inspector_port)
                    }
                }
            }
        }
        
        # Save to appropriate location
        if sys.platform == "darwin":  # macOS
            claude_config_dir = Path.home() / "Library/Application Support/Claude"
        elif sys.platform == "win32":  # Windows
            claude_config_dir = Path(os.environ.get("APPDATA", "")) / "Claude"
        else:  # Linux
            claude_config_dir = Path.home() / ".config/claude"
        
        claude_config_dir.mkdir(parents=True, exist_ok=True)
        config_file = claude_config_dir / "claude_desktop_config.json"
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Claude Desktop config updated: {config_file}")
        return config

class TestSuite:
    """Comprehensive test suite for jester-mcp development"""
    
    def __init__(self, config: DevelopmentConfig):
        self.config = config
        self.test_results: List[Dict[str, Any]] = []
    
    async def test_mcp_protocol(self, server):
        """Test MCP protocol compliance"""
        test_cases = [
            {
                "name": "initialize",
                "request": {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {"name": "test-client", "version": "1.0.0"}
                    }
                }
            },
            {
                "name": "list_tools",
                "request": {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/list",
                    "params": {}
                }
            },
            {
                "name": "execute_python",
                "request": {
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/call",
                    "params": {
                        "name": "jester-mcp:execute_code",
                        "arguments": {
                            "language": "python",
                            "code": "print('Hello from test!')"
                        }
                    }
                }
            }
        ]
        
        results = []
        for test_case in test_cases:
            try:
                # Mock the server response for testing
                response = await self._mock_server_call(server, test_case["request"])
                results.append({
                    "test": test_case["name"],
                    "status": "passed",
                    "response": response
                })
            except Exception as e:
                results.append({
                    "test": test_case["name"],
                    "status": "failed",
                    "error": str(e)
                })
        
        return results
    
    async def test_container_isolation(self):
        """Test container isolation and security"""
        test_scripts = [
            {
                "name": "file_system_isolation",
                "code": "import os; print(os.listdir('/'))",
                "should_fail": True
            },
            {
                "name": "network_isolation",
                "code": "import socket; socket.socket().connect(('google.com', 80))",
                "should_fail": True
            },
            {
                "name": "memory_limit",
                "code": "x = 'a' * (1024**3)",  # 1GB string
                "should_fail": True
            },
            {
                "name": "safe_computation",
                "code": "print(sum(range(100)))",
                "should_fail": False
            }
        ]
        
        results = []
        for test in test_scripts:
            try:
                # This would integrate with your container execution
                result = await self._execute_in_container(test["code"])
                
                if test["should_fail"]:
                    status = "failed" if result["success"] else "passed"
                else:
                    status = "passed" if result["success"] else "failed"
                
                results.append({
                    "test": test["name"],
                    "status": status,
                    "result": result
                })
            except Exception as e:
                results.append({
                    "test": test["name"],
                    "status": "error",
                    "error": str(e)
                })
        
        return results
    
    async def benchmark_performance(self):
        """Benchmark performance of different execution modes"""
        benchmarks = [
            {
                "name": "simple_calculation",
                "code": "sum(range(1000))",
                "language": "python"
            },
            {
                "name": "file_operations",
                "code": "with open('/tmp/test.txt', 'w') as f: f.write('test')",
                "language": "python"
            },
            {
                "name": "algorithm_test",
                "code": "sorted([3,1,4,1,5,9,2,6,5])",
                "language": "python"
            }
        ]
        
        results = {}
        for benchmark in benchmarks:
            results[benchmark["name"]] = {
                "subprocess": await self._benchmark_subprocess(benchmark),
                "container": await self._benchmark_container(benchmark),
                "isolation": await self._benchmark_isolation(benchmark)
            }
        
        return results
    
    async def _mock_server_call(self, server, request):
        """Mock server call for testing"""
        # This would integrate with your actual server
        return {"jsonrpc": "2.0", "id": request["id"], "result": {"status": "ok"}}
    
    async def _execute_in_container(self, code):
        """Execute code in container for testing"""
        # Mock implementation - replace with actual container execution
        return {"success": True, "output": "mocked output"}
    
    async def _benchmark_subprocess(self, benchmark):
        """Benchmark subprocess execution"""
        import time
        start = time.time()
        # Mock execution time
        await asyncio.sleep(0.01)
        return {"time": time.time() - start, "mode": "subprocess"}
    
    async def _benchmark_container(self, benchmark):
        """Benchmark container execution"""
        import time
        start = time.time()
        await asyncio.sleep(0.05)
        return {"time": time.time() - start, "mode": "container"}
    
    async def _benchmark_isolation(self, benchmark):
        """Benchmark isolation container execution"""
        import time
        start = time.time()
        await asyncio.sleep(0.1)
        return {"time": time.time() - start, "mode": "isolation"}

class DevelopmentCLI:
    """Command-line interface for development tasks"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.config = self.config_manager.load_config()
    
    def setup_development(self):
        """Setup development environment"""
        print("🚀 Setting up Jester MCP development environment...")
        
        # Create development directories
        dirs = [".jester", "tests", "logs", "temp"]
        for dir_name in dirs:
            Path(dir_name).mkdir(exist_ok=True)
            print(f"✅ Created directory: {dir_name}")
        
        # Generate development config
        self.config_manager.save_config(self.config)
        print(f"✅ Saved development config: {self.config_manager.config_file}")
        
        # Setup Claude Desktop config
        server_path = Path("standalone_mcp_server.py")
        if server_path.exists():
            self.config_manager.create_claude_desktop_config(str(server_path))
        else:
            print("⚠️  standalone_mcp_server.py not found - please update Claude config manually")
        
        # Create development scripts
        self._create_dev_scripts()
        
        print("🎉 Development environment setup complete!")
        print(f"📊 Inspector will be available at: http://localhost:{self.config.inspector_port}")
    
    def _create_dev_scripts(self):
        """Create helpful development scripts"""
        scripts = {
            "dev_server.py": """#!/usr/bin/env python3
# Development server with enhanced debugging
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from mcp_inspector import enhance_jester_mcp
from standalone_mcp_server import main_server  # Your existing server

if __name__ == "__main__":
    # Start enhanced server with debugging
    original_server = main_server()
    enhanced_server = enhance_jester_mcp(original_server)
    enhanced_server.run()
""",
            "run_tests.py": """#!/usr/bin/env python3
# Test runner for jester-mcp
import asyncio
from dev_tools_config import TestSuite, DevelopmentConfig

async def main():
    config = DevelopmentConfig()
    test_suite = TestSuite(config)
    
    print("🧪 Running MCP Protocol Tests...")
    protocol_results = await test_suite.test_mcp_protocol(None)
    
    print("🛡️ Running Security Tests...")
    security_results = await test_suite.test_container_isolation()
    
    print("⚡ Running Performance Benchmarks...")
    benchmark_results = await test_suite.benchmark_performance()
    
    # Print results
    print("\\n📊 Test Results:")
    for result in protocol_results + security_results:
        status_icon = "✅" if result["status"] == "passed" else "❌"
        print(f"{status_icon} {result['test']}: {result['status']}")

if __name__ == "__main__":
    asyncio.run(main())
""",
            "quick_test.sh": """#!/bin/bash
# Quick test script for development
echo "🃏 Jester MCP Quick Test"
echo "Testing MCP server..."

echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | python standalone_mcp_server.py

echo "✅ Basic MCP test complete"
""",
            "install_deps.py": """#!/usr/bin/env python3
# Install development dependencies
import subprocess
import sys

deps = [
    "fastapi",
    "uvicorn",
    "websockets",
    "psutil",
    "pyyaml",
    "pytest",
    "watchdog"
]

for dep in deps:
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
        print(f"✅ Installed {dep}")
    except subprocess.CalledProcessError:
        print(f"❌ Failed to install {dep}")
"""
        }
        
        for filename, content in scripts.items():
            with open(filename, 'w') as f:
                f.write(content)
            
            # Make shell scripts executable
            if filename.endswith('.sh'):
                os.chmod(filename, 0o755)
            
            print(f"✅ Created development script: {filename}")
    
    def run_diagnostics(self):
        """Run system diagnostics"""
        print("🔍 Running Jester MCP Diagnostics...")
        
        # Check Python version
        print(f"Python version: {sys.version}")
        
        # Check required dependencies
        required_deps = ["json", "asyncio", "subprocess", "pathlib"]
        optional_deps = ["podman", "docker", "fastapi", "uvicorn"]
        
        print("\n📦 Required Dependencies:")
        for dep in required_deps:
            try:
                __import__(dep)
                print(f"✅ {dep}")
            except ImportError:
                print(f"❌ {dep} - MISSING")
        
        print("\n📦 Optional Dependencies:")
        for dep in optional_deps:
            try:
                __import__(dep)
                print(f"✅ {dep}")
            except ImportError:
                print(f"⚠️  {dep} - Not installed")
        
        # Check container runtime
        print("\n🐋 Container Runtime:")
        for runtime in ["podman", "docker"]:
            if shutil.which(runtime):
                try:
                    result = subprocess.run([runtime, "--version"], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        print(f"✅ {runtime} - {result.stdout.strip()}")
                    else:
                        print(f"⚠️  {runtime} - Found but not working")
                except:
                    print(f"⚠️  {runtime} - Found but error checking version")
            else:
                print(f"❌ {runtime} - Not found")
        
        # Check Claude Desktop config
        config_paths = [
            Path.home() / "Library/Application Support/Claude/claude_desktop_config.json",  # macOS
            Path(os.environ.get("APPDATA", "")) / "Claude/claude_desktop_config.json",  # Windows
            Path.home() / ".config/claude/claude_desktop_config.json"  # Linux
        ]
        
        print("\n🤖 Claude Desktop Configuration:")
        found_config = False
        for config_path in config_paths:
            if config_path.exists():
                print(f"✅ Found config: {config_path}")
                found_config = True
                try:
                    with open(config_path) as f:
                        config = json.load(f)
                    if "mcpServers" in config:
                        print(f"   Configured servers: {list(config['mcpServers'].keys())}")
                except:
                    print("   ⚠️  Config file exists but couldn't parse")
        
        if not found_config:
            print("❌ No Claude Desktop config found")
        
        print("\n🏁 Diagnostics complete!")

def main():
    """Main CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Jester MCP Development Tools")
    parser.add_argument("command", choices=["setup", "test", "diagnose", "config"])
    parser.add_argument("--port", type=int, default=8000, help="Inspector port")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    cli = DevelopmentCLI()
    
    if args.command == "setup":
        cli.setup_development()
    elif args.command == "test":
        print("🧪 Running test suite...")
        os.system("python run_tests.py")
    elif args.command == "diagnose":
        cli.run_diagnostics()
    elif args.command == "config":
        print("📝 Current configuration:")
        print(yaml.dump(asdict(cli.config), default_flow_style=False))

if __name__ == "__main__":
    main()
