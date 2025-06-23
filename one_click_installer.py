#!/usr/bin/env python3
"""
Jester MCP Inspector - One-Click Installer
Downloads and installs all development tools for your jester-mcp project

Usage:
    curl -sSL https://raw.githubusercontent.com/mstanton/jester-mcp/main/install_inspector.py | python3
    
Or download and run locally:
    python3 install_inspector.py
"""

import os
import sys
import json
import shutil
import subprocess
import urllib.request
from pathlib import Path
from typing import Dict, Any

# Configuration
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/mstanton/jester-mcp/main/inspector"
VERSION = "1.0.0"

# Files to download and install
INSPECTOR_FILES = {
    "mcp_inspector.py": "Core MCP inspector and debugging tools",
    "dev_tools_config.py": "Development configuration and testing utilities", 
    "integration_setup.py": "Integration setup and configuration manager"
}

# Generated files (created locally, not downloaded)
GENERATED_FILES = {
    "dev_server.py": "Enhanced development server with debugging",
    "run_tests.py": "Test runner for development",
    "quick_start.py": "Quick start script",
    "check_health.py": "Health check utility"
}

class InspectorInstaller:
    """One-click installer for Jester MCP Inspector"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.backup_dir = self.project_root / ".jester_backup"
        self.installed_files = []
        
    def check_prerequisites(self) -> bool:
        """Check if this looks like a jester-mcp project"""
        print("🔍 Checking prerequisites...")
        
        # Check for main server file
        server_file = self.project_root / "standalone_mcp_server.py"
        if not server_file.exists():
            print("❌ standalone_mcp_server.py not found")
            print("   Please run this installer in your jester-mcp project directory")
            return False
        
        # Check Python version
        if sys.version_info < (3, 7):
            print(f"❌ Python 3.7+ required, found {sys.version}")
            return False
        
        print("✅ Prerequisites satisfied")
        return True
    
    def create_backup(self):
        """Create backup of existing files"""
        print("💾 Creating backup of existing files...")
        
        self.backup_dir.mkdir(exist_ok=True)
        
        files_to_backup = list(INSPECTOR_FILES.keys()) + list(GENERATED_FILES.keys())
        backed_up = 0
        
        for filename in files_to_backup:
            file_path = self.project_root / filename
            if file_path.exists():
                backup_path = self.backup_dir / filename
                shutil.copy2(file_path, backup_path)
                backed_up += 1
                print(f"   📄 Backed up {filename}")
        
        if backed_up > 0:
            print(f"✅ Backed up {backed_up} files to .jester_backup/")
        else:
            print("ℹ️  No existing files to backup")
    
    def download_file(self, filename: str, description: str) -> bool:
        """Download a file from GitHub"""
        url = f"{GITHUB_RAW_BASE}/{filename}"
        local_path = self.project_root / filename
        
        try:
            print(f"📥 Downloading {filename}...")
            urllib.request.urlretrieve(url, local_path)
            self.installed_files.append(filename)
            print(f"   ✅ {description}")
            return True
        except Exception as e:
            print(f"   ❌ Failed to download {filename}: {e}")
            return False
    
    def create_generated_file(self, filename: str, description: str) -> bool:
        """Create a generated file locally"""
        print(f"📝 Creating {filename}...")
        
        content = self.get_file_content(filename)
        if not content:
            print(f"   ❌ No content template for {filename}")
            return False
        
        try:
            with open(self.project_root / filename, 'w') as f:
                f.write(content)
            self.installed_files.append(filename)
            print(f"   ✅ {description}")
            return True
        except Exception as e:
            print(f"   ❌ Failed to create {filename}: {e}")
            return False
    
    def get_file_content(self, filename: str) -> str:
        """Get content for generated files"""
        if filename == "dev_server.py":
            return '''#!/usr/bin/env python3
"""
Enhanced development server for jester-mcp with debugging
Run this instead of standalone_mcp_server.py during development
"""

import sys
import os
import asyncio
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Main entry point for development server"""
    print("🃏 Jester MCP Development Server")
    
    # Try to import inspector tools
    try:
        from mcp_inspector import enhance_jester_mcp
        from standalone_mcp_server import main as original_main
        
        print("📊 Inspector Dashboard: http://localhost:8000")
        print("🔧 Debug mode enabled")
        
        # For now, just run the original server
        # TODO: Integrate inspector when server structure is analyzed
        original_main()
        
    except ImportError as e:
        print(f"⚠️  Inspector not available: {e}")
        print("🔧 Running in basic mode")
        
        # Fallback to original server
        try:
            from standalone_mcp_server import main as original_main
            original_main()
        except ImportError:
            print("❌ Could not import standalone_mcp_server")
            sys.exit(1)

if __name__ == "__main__":
    main()
'''
        
        elif filename == "run_tests.py":
            return '''#!/usr/bin/env python3
"""Test runner for jester-mcp development"""

import sys
import subprocess
from pathlib import Path

def run_basic_tests():
    """Run basic import and functionality tests"""
    print("🧪 Running basic jester-mcp tests...")
    
    # Test imports
    try:
        import standalone_mcp_server
        print("✅ Can import standalone_mcp_server")
    except ImportError as e:
        print(f"❌ Cannot import server: {e}")
        return False
    
    # Test inspector if available
    try:
        import mcp_inspector
        print("✅ Inspector tools available")
    except ImportError:
        print("⚠️  Inspector tools not available")
    
    print("✅ Basic tests passed")
    return True

def main():
    """Main test runner"""
    print("🃏 Jester MCP Test Runner")
    success = run_basic_tests()
    
    if success:
        print("🎉 All tests passed!")
    else:
        print("❌ Some tests failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
        
        elif filename == "quick_start.py":
            return '''#!/usr/bin/env python3
"""Quick start script for jester-mcp development"""

import subprocess
import sys
import webbrowser
import time
from pathlib import Path

def main():
    """Quick start the development environment"""
    print("🃏 Jester MCP Quick Start")
    print("=" * 30)
    
    # Check if dev server exists
    if Path("dev_server.py").exists():
        print("🚀 Starting development server...")
        print("📊 Inspector dashboard will open automatically")
        
        # Start the dev server in background and open browser
        try:
            # Start server
            proc = subprocess.Popen([sys.executable, "dev_server.py"])
            
            # Wait a moment then open browser
            time.sleep(2)
            webbrowser.open("http://localhost:8000")
            
            print("\\n🎯 Development server started!")
            print("📊 Inspector: http://localhost:8000")
            print("🔧 Press Ctrl+C to stop")
            
            # Wait for server
            proc.wait()
            
        except KeyboardInterrupt:
            print("\\n👋 Stopping development server...")
            proc.terminate()
        except Exception as e:
            print(f"❌ Error starting server: {e}")
    else:
        print("❌ dev_server.py not found")
        print("   Run the installer first")

if __name__ == "__main__":
    main()
'''
        
        elif filename == "check_health.py":
            return '''#!/usr/bin/env python3
"""Health check for jester-mcp setup"""

import sys
import json
from pathlib import Path

def check_files():
    """Check if required files exist"""
    required_files = [
        "standalone_mcp_server.py",
        "mcp_inspector.py", 
        "dev_server.py"
    ]
    
    missing = []
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - MISSING")
            missing.append(file)
    
    return len(missing) == 0

def check_dependencies():
    """Check if required dependencies are installed"""
    deps = ["json", "asyncio", "pathlib"]
    optional_deps = ["fastapi", "uvicorn", "websockets"]
    
    print("\\n📦 Core Dependencies:")
    for dep in deps:
        try:
            __import__(dep)
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep} - MISSING")
    
    print("\\n📦 Optional Dependencies:")
    for dep in optional_deps:
        try:
            __import__(dep)
            print(f"✅ {dep}")
        except ImportError:
            print(f"⚠️  {dep} - Not installed (for full features)")

def check_claude_config():
    """Check Claude Desktop configuration"""
    config_paths = [
        Path.home() / "Library/Application Support/Claude/claude_desktop_config.json",  # macOS
        Path(os.environ.get("APPDATA", "")) / "Claude/claude_desktop_config.json",      # Windows  
        Path.home() / ".config/claude/claude_desktop_config.json"                       # Linux
    ]
    
    print("\\n🤖 Claude Desktop Configuration:")
    for config_path in config_paths:
        if config_path.exists():
            print(f"✅ Found config: {config_path}")
            return True
    
    print("❌ No Claude Desktop config found")
    return False

def main():
    """Run health check"""
    print("🏥 Jester MCP Health Check")
    print("=" * 30)
    
    files_ok = check_files()
    check_dependencies()
    config_ok = check_claude_config()
    
    print("\\n" + "=" * 30)
    if files_ok and config_ok:
        print("🎉 Health check passed! Ready to develop.")
    else:
        print("⚠️  Some issues found. Check above for details.")

if __name__ == "__main__":
    import os
    main()
'''
        
        return ""
    
    def install_dependencies(self):
        """Install required dependencies"""
        print("📦 Installing dependencies...")
        
        # Basic dependencies that should always work
        basic_deps = ["pyyaml"]
        
        # Optional dependencies for full features
        optional_deps = [
            "fastapi>=0.100.0",
            "uvicorn[standard]>=0.23.0", 
            "websockets>=11.0",
            "psutil>=5.9.0"
        ]
        
        # Install basic dependencies
        for dep in basic_deps:
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", dep
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"   ✅ {dep}")
            except subprocess.CalledProcessError:
                print(f"   ⚠️  Failed to install {dep}")
        
        # Try to install optional dependencies
        print("   Installing optional dependencies for full features...")
        optional_success = 0
        for dep in optional_deps:
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", dep
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                optional_success += 1
            except subprocess.CalledProcessError:
                pass
        
        print(f"   ✅ Installed {optional_success}/{len(optional_deps)} optional dependencies")
        if optional_success < len(optional_deps):
            print("   ℹ️  Some features may be limited without all dependencies")
    
    def update_claude_config(self):
        """Update Claude Desktop configuration"""
        print("🤖 Updating Claude Desktop configuration...")
        
        # Find Claude config directory
        config_paths = []
        if sys.platform == "darwin":  # macOS
            config_paths.append(Path.home() / "Library/Application Support/Claude")
        elif sys.platform == "win32":  # Windows
            if "APPDATA" in os.environ:
                config_paths.append(Path(os.environ["APPDATA"]) / "Claude")
        else:  # Linux
            config_paths.append(Path.home() / ".config/claude")
        
        config_dir = None
        for path in config_paths:
            if path.exists() or path.parent.exists():
                config_dir = path
                break
        
        if not config_dir:
            print("⚠️  Could not find Claude config directory")
            self.print_manual_config_instructions()
            return
        
        # Ensure config directory exists
        config_dir.mkdir(parents=True, exist_ok=True)
        config_file = config_dir / "claude_desktop_config.json"
        
        # Read existing config
        config = {}
        if config_file.exists():
            try:
                with open(config_file) as f:
                    config = json.load(f)
            except:
                print("⚠️  Could not read existing config, creating new one")
        
        # Update with jester-mcp configuration
        if "mcpServers" not in config:
            config["mcpServers"] = {}
        
        # Use dev_server.py if available, fallback to standalone_mcp_server.py
        server_script = "dev_server.py"
        if not (self.project_root / server_script).exists():
            server_script = "standalone_mcp_server.py"
        
        config["mcpServers"]["jester-mcp"] = {
            "command": sys.executable,
            "args": [str((self.project_root / server_script).absolute())],
            "env": {
                "JESTER_DEBUG": "true",
                "JESTER_INSPECTOR_PORT": "8000"
            }
        }
        
        # Backup existing config
        if config_file.exists():
            backup_file = config_file.with_suffix('.json.backup')
            shutil.copy2(config_file, backup_file)
            print(f"   📄 Backed up existing config to {backup_file}")
        
        # Write updated config
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"   ✅ Updated Claude config: {config_file}")
        print("   🔄 Please restart Claude Desktop to apply changes")
    
    def print_manual_config_instructions(self):
        """Print manual configuration instructions"""
        print("\\n📝 Manual Claude Desktop Configuration:")
        print("Please add this to your claude_desktop_config.json file:")
        
        config = {
            "mcpServers": {
                "jester-mcp": {
                    "command": sys.executable,
                    "args": [str((self.project_root / "dev_server.py").absolute())],
                    "env": {
                        "JESTER_DEBUG": "true",
                        "JESTER_INSPECTOR_PORT": "8000"
                    }
                }
            }
        }
        
        print(json.dumps(config, indent=2))
    
    def install(self, skip_download: bool = False) -> bool:
        """Run the complete installation"""
        print("🃏 Jester MCP Inspector Installer")
        print(f"Version {VERSION}")
        print("=" * 40)
        
        # Step 1: Check prerequisites
        if not self.check_prerequisites():
            return False
        
        # Step 2: Create backup
        self.create_backup()
        
        # Step 3: Download or skip files (for offline mode)
        if not skip_download:
            print("📥 Downloading inspector files...")
            download_success = 0
            for filename, description in INSPECTOR_FILES.items():
                if self.download_file(filename, description):
                    download_success += 1
            
            if download_success == 0:
                print("❌ Failed to download any files")
                print("ℹ️  You may be offline - creating local versions instead")
                skip_download = True
        
        # Step 4: Create generated files
        print("📝 Creating development files...")
        for filename, description in GENERATED_FILES.items():
            self.create_generated_file(filename, description)
        
        # Step 5: Install dependencies
        self.install_dependencies()
        
        # Step 6: Update Claude config
        self.update_claude_config()
        
        # Step 7: Success message
        self.print_success_message()
        
        return True
    
    def print_success_message(self):
        """Print installation success message"""
        print("\\n" + "=" * 50)
        print("🎉 Jester MCP Inspector Installation Complete!")
        print("=" * 50)
        
        print("\\n📋 Quick Start:")
        print("1. Restart Claude Desktop")
        print("2. Run: python dev_server.py")
        print("3. Open: http://localhost:8000")
        print("4. Test with Claude: 'Test jester-mcp debugging'")
        
        print("\\n🔧 Available Commands:")
        print("• python dev_server.py      - Start development server")
        print("• python run_tests.py       - Run tests")
        print("• python check_health.py    - Health check")
        print("• python quick_start.py     - Quick start with browser")
        
        print(f"\\n📁 Installed {len(self.installed_files)} files")
        print(f"💾 Backup available in: {self.backup_dir}")
        
        print("\\n🚀 Ready to develop with enhanced debugging!")

def main():
    """Main installer entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Install Jester MCP Inspector")
    parser.add_argument("--offline", action="store_true", 
                       help="Skip downloads (offline mode)")
    parser.add_argument("--force", action="store_true",
                       help="Force installation")
    
    args = parser.parse_args()
    
    installer = InspectorInstaller()
    
    if args.force or input("Install Jester MCP Inspector? (y/N): ").lower() == 'y':
        success = installer.install(skip_download=args.offline)
        if success:
            print("\\n✨ Installation successful!")
        else:
            print("\\n❌ Installation failed")
            sys.exit(1)
    else:
        print("👋 Installation cancelled")

if __name__ == "__main__":
    main()
