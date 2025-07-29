#!/usr/bin/env python3
"""
RagFlow Enhanced Development Starter - Full Stack Support
Manages both Backend AND Frontend with smart rebuild detection
"""

import subprocess
import sys
import os
import json
import hashlib
import time
import signal
import requests
import socket
from pathlib import Path
from typing import Optional, Dict, Any, List

class Colors:
    """ANSI color codes for cross-platform terminal"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'

def print_colored(text: str, color: str = Colors.RESET):
    """Print colored text"""
    print(f"{color}{text}{Colors.RESET}")

def run_command(command: str, cwd: Optional[str] = None, check: bool = True, capture_output: bool = True) -> Optional[subprocess.CompletedProcess]:
    """Execute a command and return the result"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd, 
            check=check,
            capture_output=capture_output,
            text=True,
            timeout=300  # 5 minute timeout
        )
        return result
    except subprocess.CalledProcessError as e:
        if capture_output:
            print_colored(f"❌ Error executing '{command}': {e}", Colors.RED)
            if e.stdout:
                print(f"STDOUT: {e.stdout}")
            if e.stderr:
                print(f"STDERR: {e.stderr}")
        return None
    except subprocess.TimeoutExpired:
        print_colored(f"⏰ Command timed out: {command}", Colors.YELLOW)
        return None

def get_file_hash(filepath: str) -> Optional[str]:
    """Create SHA256 hash of a file"""
    try:
        with open(filepath, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except FileNotFoundError:
        return None

def get_directory_hash(directory: str, patterns: List[str]) -> str:
    """Get hash of directory contents matching patterns"""
    hash_content = ""
    dir_path = Path(directory)
    
    if not dir_path.exists():
        return ""
    
    for pattern in patterns:
        for file_path in dir_path.rglob(pattern):
            if file_path.is_file():
                try:
                    hash_content += str(file_path.stat().st_mtime)
                    hash_content += str(file_path.stat().st_size)
                except:
                    continue
    
    return hashlib.sha256(hash_content.encode()).hexdigest()

def check_docker_running() -> bool:
    """Check if Docker is running"""
    try:
        result = run_command("docker --version", capture_output=True)
        if result and result.returncode == 0:
            # Test Docker daemon
            result = run_command("docker ps", capture_output=True)
            return result is not None and result.returncode == 0
    except:
        pass
    return False

def get_change_detection() -> Dict[str, str]:
    """Get current hashes of important files/directories"""
    hashes = {}
    
    # Backend files
    backend_files = [
        "backend/requirements.txt",
        "backend/Dockerfile.dev",
        "docker/docker-compose.dev.yml"
    ]
    
    for file_path in backend_files:
        if Path(file_path).exists():
            hashes[file_path] = get_file_hash(file_path) or ""
    
    # Backend source code hash
    hashes["backend_src"] = get_directory_hash("backend/app", ["*.py"])
    
    # Frontend files
    frontend_files = [
        "frontend/package.json",
        "frontend/package-lock.json",
        "frontend/Dockerfile.dev",
        "frontend/next.config.ts",
        "frontend/tailwind.config.ts"
    ]
    
    for file_path in frontend_files:
        if Path(file_path).exists():
            hashes[file_path] = get_file_hash(file_path) or ""
    
    # Frontend source code hash
    hashes["frontend_src"] = get_directory_hash("frontend/src", ["*.tsx", "*.ts", "*.js", "*.jsx"])
    
    return hashes

def load_stored_hashes() -> Dict[str, str]:
    """Load stored hashes from cache file"""
    cache_file = Path(".dev_cache.json")
    if cache_file.exists():
        try:
            return json.loads(cache_file.read_text())
        except:
            return {}
    return {}

def store_hashes(hashes: Dict[str, str]):
    """Store hashes to cache file"""
    cache_file = Path(".dev_cache.json")
    cache_file.write_text(json.dumps(hashes, indent=2))

def needs_rebuild() -> Dict[str, bool]:
    """Determine what needs rebuilding"""
    current_hashes = get_change_detection()
    stored_hashes = load_stored_hashes()
    
    needs_rebuild = {
        "backend": False,
        "frontend": False,
        "full_restart": False
    }
    
    # Check backend changes
    backend_keys = [k for k in current_hashes.keys() if k.startswith("backend") or k == "docker/docker-compose.dev.yml"]
    for key in backend_keys:
        if current_hashes.get(key) != stored_hashes.get(key):
            needs_rebuild["backend"] = True
            break
    
    # Check frontend changes
    frontend_keys = [k for k in current_hashes.keys() if k.startswith("frontend")]
    for key in frontend_keys:
        if current_hashes.get(key) != stored_hashes.get(key):
            needs_rebuild["frontend"] = True
            break
    
    # Check for docker-compose changes (requires full restart)
    if current_hashes.get("docker/docker-compose.dev.yml") != stored_hashes.get("docker/docker-compose.dev.yml"):
        needs_rebuild["full_restart"] = True
    
    return needs_rebuild

def get_container_status() -> Dict[str, str]:
    """Get status of all containers"""
    result = run_command("docker compose -f docker/docker-compose.dev.yml ps", capture_output=True)
    containers = {}
    
    if result and result.returncode == 0:
        lines = result.stdout.strip().split('\n')[1:]  # Skip header
        for line in lines:
            if line.strip():
                parts = line.split()
                if len(parts) >= 2:
                    name = parts[0]
                    # Extract service name from container name
                    if "ragflow-" in name:
                        service = name.replace("ragflow-", "")
                        containers[service] = " ".join(parts[1:])
    
    return containers

def wait_for_service(url: str, service_name: str, timeout: int = 60) -> bool:
    """Wait for a service to become available"""
    print_colored(f"⏳ Waiting for {service_name}...", Colors.YELLOW)
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code < 500:  # Accept any non-server-error response
                print_colored(f"✅ {service_name} is ready!", Colors.GREEN)
                return True
        except:
            pass
        
        time.sleep(2)
    
    print_colored(f"⚠️  {service_name} may not be ready yet", Colors.YELLOW)
    return False

def start_services(rebuild_config: Dict[str, bool]) -> bool:
    """Start or restart services based on rebuild configuration"""
    compose_file = "docker/docker-compose.dev.yml"
    
    if rebuild_config["full_restart"]:
        print_colored("🔄 Full restart required - stopping all services...", Colors.BLUE)
        
        # Stop all services
        result = run_command(f"docker compose -f {compose_file} down", capture_output=False)
        if not result:
            return False
        
        print_colored("🚀 Starting all services with build...", Colors.BLUE)
        result = run_command(f"docker compose -f {compose_file} up --build -d", capture_output=False)
        return result is not None and result.returncode == 0
    
    elif rebuild_config["backend"] or rebuild_config["frontend"]:
        services_to_rebuild = []
        
        if rebuild_config["backend"]:
            services_to_rebuild.append("backend")
            print_colored("🔄 Backend changes detected", Colors.YELLOW)
        
        if rebuild_config["frontend"]:
            services_to_rebuild.append("frontend")
            print_colored("🔄 Frontend changes detected", Colors.YELLOW)
        
        print_colored(f"🚀 Rebuilding services: {', '.join(services_to_rebuild)}", Colors.BLUE)
        
        for service in services_to_rebuild:
            print_colored(f"🔨 Rebuilding {service}...", Colors.BLUE)
            result = run_command(f"docker compose -f {compose_file} up --build {service} -d", capture_output=False)
            if not result or result.returncode != 0:
                print_colored(f"❌ Failed to rebuild {service}", Colors.RED)
                return False
        
        return True
    
    else:
        # Just start services if they're not running
        containers = get_container_status()
        required_services = ["backend", "frontend", "postgres", "redis", "qdrant"]
        
        missing_services = []
        for service in required_services:
            if service not in containers or "Up" not in containers[service]:
                missing_services.append(service)
        
        if missing_services:
            print_colored(f"🚀 Starting services: {', '.join(missing_services)}", Colors.BLUE)
            result = run_command(f"docker compose -f {compose_file} up -d", capture_output=False)
            return result is not None and result.returncode == 0
        else:
            print_colored("✅ All services are already running", Colors.GREEN)
            return True

def show_service_status():
    """Show detailed service status"""
    print_colored("\n🌐 Service Status:", Colors.CYAN)
    
    services = {
        "Backend API": "http://localhost:8000/ping",
        "Frontend App": "http://localhost:3000",
        "Qdrant Dashboard": "http://localhost:6333/dashboard"
    }
    
    for name, url in services.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code < 500:
                print_colored(f"   ✅ {name}: Running", Colors.GREEN)
            else:
                print_colored(f"   ⚠️  {name}: Service Error", Colors.YELLOW)
        except:
            print_colored(f"   ❌ {name}: Not Available", Colors.RED)

def show_urls():
    """Show service URLs"""
    print_colored("\n🔗 Service URLs:", Colors.CYAN)
    print("   🖥️  Frontend:         http://localhost:3000")
    print("   🚀 Backend API:      http://localhost:8000")
    print("   📚 API Docs:         http://localhost:8000/docs")
    print("   🔍 Qdrant Dashboard: http://localhost:6333/dashboard")
    print("   🗄️  PostgreSQL:       localhost:5432 (ragflow/ragflow)")

def show_success_message():
    """Show success message with next steps"""
    print_colored("\n🎉 RagFlow Development Environment Ready!", Colors.GREEN + Colors.BOLD)
    print_colored("=" * 60, Colors.GREEN)
    
    print_colored("\n🚀 Next Steps:", Colors.CYAN)
    print("   1. 🖥️  Open Frontend: http://localhost:3000")
    print("   2. 📚 Check API Docs: http://localhost:8000/docs")
    print("   3. 📁 Upload documents via frontend")
    print("   4. 🔍 Test semantic search")
    
    print_colored("\n💡 Development Tips:", Colors.YELLOW)
    print("   • Frontend auto-reloads on code changes")
    print("   • Backend auto-reloads on code changes")
    print("   • Use 'docker compose -f docker/docker-compose.dev.yml logs -f' for logs")
    print("   • API is available at http://localhost:8000")

def cleanup_on_exit(signum, frame):
    """Cleanup on program exit"""
    print_colored("\n\n👋 Development session ended", Colors.YELLOW)
    print("   Containers continue running in background")
    print("   Use 'docker compose -f docker/docker-compose.dev.yml down' to stop all services")
    sys.exit(0)

def main():
    """Main function"""
    # Signal handler for clean shutdown
    signal.signal(signal.SIGINT, cleanup_on_exit)
    signal.signal(signal.SIGTERM, cleanup_on_exit)
    
    print_colored("🚀 RagFlow Full-Stack Development Setup", Colors.BOLD + Colors.GREEN)
    print_colored("=" * 60, Colors.GREEN)
    
    # Check Docker
    if not check_docker_running():
        print_colored("❌ Docker is not available! Please start Docker Desktop.", Colors.RED)
        return 1
    
    print_colored("✅ Docker is running", Colors.GREEN)
    
    # Check what needs rebuilding
    print_colored("\n🔍 Checking for changes...", Colors.BLUE)
    rebuild_config = needs_rebuild()
    
    if any(rebuild_config.values()):
        print_colored("🔄 Changes detected, rebuilding services...", Colors.YELLOW)
    else:
        print_colored("✅ No changes detected", Colors.GREEN)
    
    # Start services
    print_colored("\n🚀 Managing services...", Colors.BLUE)
    if not start_services(rebuild_config):
        print_colored("❌ Failed to start services", Colors.RED)
        return 1
    
    # Wait for critical services
    print_colored("\n⏳ Waiting for services to be ready...", Colors.BLUE)
    backend_ready = wait_for_service("http://localhost:8000/ping", "Backend API", 60)
    frontend_ready = wait_for_service("http://localhost:3000", "Frontend App", 60)
    
    # Store current hashes for next run
    current_hashes = get_change_detection()
    store_hashes(current_hashes)
    
    # Show status
    show_service_status()
    show_urls()
    
    if backend_ready and frontend_ready:
        show_success_message()
    else:
        print_colored("\n⚠️  Some services may still be starting up", Colors.YELLOW)
        print_colored("   Check the URLs above in a few moments", Colors.CYAN)
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        cleanup_on_exit(None, None)
    except Exception as e:
        print_colored(f"\n❌ Unexpected error: {e}", Colors.RED)
        sys.exit(1)