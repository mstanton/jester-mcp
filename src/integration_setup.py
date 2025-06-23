#!/usr/bin/env python3
"""
Easy Integration Setup for Jester MCP Inspector
One-click setup to add development tools to your existing jester-mcp project
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from typing import Optional

class JesterMCPSetup:
    """Setup and integration manager for Jester MCP development tools"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.setup_complete = False
        
    def check_environment(self) -> bool:
        """Check if we're in a jester-mcp project directory"""
        required_files = ["standalone_mcp_server.py"]
        jester_indicators = ["quantum", "container", "slash commands"]
        
        # Check for main server file
        if not (self.project_root / "standalone_mcp_server.py").exists():
            print("❌ standalone_mcp_server.py not found")
            print("   Make sure you're in the jester-mcp project directory")
            return False
        
        # Check if it looks like jester-mcp by scanning for keywords
        try:
            with open(self.project_root / "standalone_mcp_server.py") as f:
                content = f.read().lower()
            
            if any(indicator in content for indicator in jester_indicators):
                print("✅ Detected jester-mcp project")
                return True
            else:
                print("⚠️  Found standalone_mcp_server.py but doesn't look like jester-mcp")
                response = input("Continue anyway? (y/N): ").lower()
                return response == 'y'
                
        except Exception as e:
            print(f"❌ Error reading server file: {e}")
            return False
    
    def install_dependencies(self):
        """Install required dependencies for development tools"""
        print("📦 Installing development dependencies...")
        
        deps = [
            "fastapi>=0.100.0",
            "uvicorn[standard]>=0.23.0",
            "websockets>=11.0",
            "psutil>=5.9.0",
            "pyyaml>=6.0",
            "pytest>=7.0.0",
            "watchdog>=3.0.0"
        ]
        
        failed_deps = []
        for dep in deps:
            try:
                print(f"   Installing {dep}...")
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", dep
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"   ✅ {dep}")
            except subprocess.CalledProcessError:
                print(f"   ❌ Failed to install {dep}")
                failed_deps.append(dep)
        
        if failed_deps:
            print(f"\n⚠️  Some dependencies failed to install: {failed_deps}")
            print("You may need to install them manually or run with elevated privileges")
        else:
            print("✅ All dependencies installed successfully")
    
    def create_development_files(self):
        """Create the development tool files"""
        print("📁 Creating development tool files...")
        
        files_to_create = [
            "mcp_inspector.py",
            "dev_tools_config.py",
            "dev_server.py",
            "run_tests.py"
        ]
        
        # Create dev_server.py that integrates with existing server
        dev_server_content = '''#!/usr/bin/env python3
"""
Enhanced development server for jester-mcp with debugging and inspection
Run this instead of standalone_mcp_server.py during development
"""

import sys
import os
import asyncio
import threading
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import the development tools
try:
    from mcp_inspector import MCPInspector, DevelopmentServer, EnhancedMCPServer
    INSPECTOR_AVAILABLE = True
except ImportError:
    print("⚠️  MCP Inspector not available - falling back to basic server")
    INSPECTOR_AVAILABLE = False

# Import your existing server
try:
    from standalone_mcp_server import MCPServer, main
    print("✅ Loaded existing jester-mcp server")
except ImportError as e:
    print(f"❌ Could not import existing server: {e}")
    sys.exit(1)

class DevelopmentMCPServer:
    """Development wrapper for the existing MCP server"""
    
    def __init__(self):
        self.enhanced_server = None
        self.inspector_port = int(os.environ.get('JESTER_INSPECTOR_PORT', '8000'))
        
    async def run_with_inspector(self):
        """Run server with inspector if available"""
        if not INSPECTOR_AVAILABLE:
            print("🔧 Running in basic mode - install inspector dependencies for full features")
            await main()
            return
        
        print("🃏 Starting Jester MCP Development Server with Inspector...")
        print(f"📊 Inspector Dashboard: http://localhost:{self.inspector_port}")
        print("🔧 Debug mode enabled")
        
        # Create original server instance
        original_server = MCPServer()
        
        # Enhance it with inspector capabilities
        self.enhanced_server = EnhancedMCPServer(original_server)
        self.enhanced_server.wrap_handlers()
        
        # Start inspector dashboard in background
        self.enhanced_server.start_dev_server(self.inspector_port)
        
        # Run the enhanced server
        await original_server.run()

def main_dev():
    """Main entry point for development server"""
    server = DevelopmentMCPServer()
    
    try:
        asyncio.run(server.run_with_inspector())
    except KeyboardInterrupt:
        print("\\n👋 Development server stopped")
    except Exception as e:
        print(f"❌ Error running development server: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main_dev()
'''
        
        # Create run_tests.py
        run_tests_content = '''#!/usr/bin/env python3
"""
Test runner for jester-mcp development
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

try:
    from dev_tools_config import TestSuite, DevelopmentConfig
    TEST_TOOLS_AVAILABLE = True
except ImportError:
    print("⚠️  Test tools not available")
    TEST_TOOLS_AVAILABLE = False

async def run_basic_tests():
    """Run basic tests without full test suite"""
    print("🧪 Running basic jester-mcp tests...")
    
    # Test that we can import the main server
    try:
        from standalone_mcp_server import MCPServer
        print("✅ Can import MCPServer")
    except ImportError as e:
        print(f"❌ Cannot import MCPServer: {e}")
        return
    
    # Test basic functionality
    try:
        server = MCPServer()
        print("✅ Can create MCPServer instance")
    except Exception as e:
        print(f"❌ Cannot create MCPServer: {e}")
        return
    
    print("✅ Basic tests passed")

async def run_full_tests():
    """Run full test suite with development tools"""
    if not TEST_TOOLS_AVAILABLE:
        await run_basic_tests()
        return
    
    print("🧪 Running full jester-mcp test suite...")
    
    config = DevelopmentConfig()
    test_suite = TestSuite(config)
    
    print("📡 Testing MCP Protocol...")
    protocol_results = await test_suite.test_mcp_protocol(None)
    
    print("🛡️ Testing Container Security...")
    security_results = await test_suite.test_container_isolation()
    
    print("⚡ Running Performance Benchmarks...")
    benchmark_results = await test_suite.benchmark_performance()
    
    # Print results summary
    print("\\n📊 Test Results Summary:")
    all_results = protocol_results + security_results
    
    passed = sum(1 for r in all_results if r["status"] == "passed")
    failed = sum(1 for r in all_results if r["status"] == "failed")
    
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    if failed > 0:
        print("\\n❌ Failed Tests:")
        for result in all_results:
            if result["status"] == "failed":
                print(f"   - {result['test']}: {result.get('error', 'Unknown error')}")

def main():
    """Main test runner entry point"""
    try:
        asyncio.run(run_full_tests())
    except KeyboardInterrupt:
        print("\\n👋 Tests interrupted")
    except Exception as e:
        print(f"❌ Error running tests: {e}")

if __name__ == "__main__":
    main()
'''
        
        # Write the files
        files_content = {
            "dev_server.py": dev_server_content,
            "run_tests.py": run_tests_content
        }
        
        for filename, content in files_content.items():
            with open(filename, 'w') as f:
                f.write(content)
            print(f"✅ Created {filename}")
    
    def update_claude_config(self):
        """Update Claude Desktop configuration"""
        print("🤖 Updating Claude Desktop configuration...")
        
        # Determine config path based on OS
        config_paths = []
        if sys.platform == "darwin":  # macOS
            config_paths.append(Path.home() / "Library/Application Support/Claude/claude_desktop_config.json")
        elif sys.platform == "win32":  # Windows
            if "APPDATA" in os.environ:
                config_paths.append(Path(os.environ["APPDATA"]) / "Claude/claude_desktop_config.json")
        else:  # Linux
            config_paths.append(Path.home() / ".config/claude/claude_desktop_config.json")
        
        config_path = None
        for path in config_paths:
            if path.parent.exists():
                config_path = path
                break
        
        if not config_path:
            print("❌ Could not find Claude config directory")
            print("   Please update Claude Desktop config manually:")
            self._print_manual_config()
            return
        
        # Read existing config or create new one
        config = {}
        if config_path.exists():
            try:
                with open(config_path) as f:
                    config = json.load(f)
            except:
                print("⚠️  Could not read existing config, creating new one")
        
        # Update config with jester-mcp
        if "mcpServers" not in config:
            config["mcpServers"] = {}
        
        # Use dev_server.py if we're in development mode
        server_script = self.project_root / "dev_server.py"
        if not server_script.exists():
            server_script = self.project_root / "standalone_mcp_server.py"
        
        config["mcpServers"]["jester-mcp"] = {
            "command": sys.executable,
            "args": [str(server_script.absolute())],
            "env": {
                "JESTER_DEBUG": "true",
                "JESTER_INSPECTOR_PORT": "8000"
            }
        }
        
        # Backup existing config
        if config_path.exists():
            backup_path = config_path.with_suffix('.json.backup')
            shutil.copy2(config_path, backup_path)
            print(f"📄 Backed up existing config to {backup_path}")
        
        # Write updated config
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Updated Claude config: {config_path}")
        print("🔄 Please restart Claude Desktop to apply changes")
    
    def _print_manual_config(self):
        """Print manual configuration instructions"""
        server_path = self.project_root / "dev_server.py"
        if not server_path.exists():
            server_path = self.project_root / "standalone_mcp_server.py"
        
        config = {
            "mcpServers": {
                "jester-mcp": {
                    "command": sys.executable,
                    "args": [str(server_path.absolute())],
                    "env": {
                        "JESTER_DEBUG": "true",
                        "JESTER_INSPECTOR_PORT": "8000"
                    }
                }
            }
        }
        
        print("\\n📝 Manual Claude Desktop Configuration:")
        print("Add this to your claude_desktop_config.json file:")
        print(json.dumps(config, indent=2))
    
    def create_useful_scripts(self):
        """Create helpful development scripts"""
        print("📜 Creating development scripts...")
        
        scripts = {
            "quick_start.py": '''#!/usr/bin/env python3
"""Quick start script for jester-mcp development"""
import subprocess
import sys

print("🃏 Jester MCP Quick Start")
print("Starting development server with inspector...")

try:
    subprocess.run([sys.executable, "dev_server.py"])
except KeyboardInterrupt:
    print("\\n👋 Server stopped")
''',
            "check_health.py": '''#!/usr/bin/env python3
"""Health check for jester-mcp setup"""
import sys
import json
from pathlib import Path

def check_files():
    """Check required files exist"""
    required = ["standalone_mcp_server.py", "dev_server.py", "mcp_inspector.py"]
    missing = []
    
    for file in required:
        if not Path(file).exists():
            missing.append(file)
    
    if missing:
        print(f"❌ Missing files: {missing}")
        return False
    else:
        print("✅ All required files present")
        return True

def check_imports():
    """Check if we can import modules"""
    modules = ["standalone_mcp_server", "mcp_inspector"]
    failed = []
    
    for module in modules:
        try:
            __import__(module)
            print(f"✅ Can import {module}")
        except ImportError as e:
            print(f"❌ Cannot import {module}: {e}")
            failed.append(module)
    
    return len(failed) == 0

def main():
    print("🏥 Jester MCP Health Check")
    
    files_ok = check_files()
    imports_ok = check_imports()
    
    if files_ok and imports_ok:
        print("\\n🎉 Everything looks good! Ready to develop.")
    else:
        print("\\n⚠️  Some issues found. Run setup again if needed.")

if __name__ == "__main__":
    main()
'''
        }
        
        for filename, content in scripts.items():
            with open(filename, 'w') as f:
                f.write(content)
            print(f"✅ Created {filename}")
    
    def run_setup(self):
        """Run the complete setup process"""
        print("🃏 Jester MCP Inspector Setup")
        print("=" * 40)
        
        # Step 1: Check environment
        if not self.check_environment():
            print("❌ Environment check failed")
            return False
        
        # Step 2: Install dependencies
        try:
            self.install_dependencies()
        except Exception as e:
            print(f"⚠️  Dependency installation had issues: {e}")
        
        # Step 3: Create development files
        self.create_development_files()
        
        # Step 4: Update Claude config
        self.update_claude_config()
        
        # Step 5: Create useful scripts
        self.create_useful_scripts()
        
        # Step 6: Final instructions
        self.print_final_instructions()
        
        self.setup_complete = True
        return True
    
    def print_final_instructions(self):
        """Print final setup instructions"""
        print("\\n" + "=" * 50)
        print("🎉 Jester MCP Inspector Setup Complete!")
        print("=" * 50)
        
        print("\\n📋 Next Steps:")
        print("1. Restart Claude Desktop")
        print("2. Run: python dev_server.py")
        print("3. Open: http://localhost:8000 for inspector dashboard")
        print("4. Test with Claude: 'Test jester-mcp with debugging'")
        
        print("\\n🔧 Development Commands:")
        print("• python dev_server.py      - Start with debugging")
        print("• python run_tests.py       - Run test suite")
        print("• python check_health.py    - Check setup")
        print("• python quick_start.py     - Quick development start")
        
        print("\\n📊 Features Added:")
        print("• Real-time MCP message inspection")
        print("• Performance monitoring and metrics")
        print("• Enhanced error reporting and debugging")
        print("• Development dashboard with live updates")
        print("• Comprehensive test suite")
        
        print("\\n🔗 Inspector Dashboard Features:")
        print("• Live MCP protocol messages")
        print("• Performance metrics and timing")
        print("• System resource monitoring")
        print("• Error tracking and analysis")
        print("• Export debugging data")
        
        print("\\n💡 Pro Tips:")
        print("• Keep the inspector dashboard open while developing")
        print("• Use 'Toggle Recording' to pause/resume message capture")
        print("• Export debug data when reporting issues")
        print("• Check health regularly during development")

def main():
    """Main setup entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Setup Jester MCP Inspector")
    parser.add_argument("--force", action="store_true", help="Force setup even if files exist")
    parser.add_argument("--deps-only", action="store_true", help="Only install dependencies")
    args = parser.parse_args()
    
    setup = JesterMCPSetup()
    
    if args.deps_only:
        setup.install_dependencies()
        return
    
    if args.force or input("Setup Jester MCP Inspector? (y/N): ").lower() == 'y':
        setup.run_setup()
    else:
        print("👋 Setup cancelled")

if __name__ == "__main__":
    main()
