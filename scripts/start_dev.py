#!/usr/bin/env python3
"""
RagFlow Backend Development Starter - Windows Compatible
Fully Windows-compatible without Unix commands
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
from typing import Optional, Dict, Any

class Colors:
    """ANSI color codes for Windows terminal"""
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
            text=True
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

def get_file_hash(filepath: str) -> Optional[str]:
    """Create SHA256 hash of a file"""
    try:
        with open(filepath, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except FileNotFoundError:
        return None

def check_docker_running() -> bool:
    """Check if Docker is running - Windows compatible"""
    result = run_command("docker info", capture_output=True)
    return result is not None and result.returncode == 0

def check_docker_compose_file() -> bool:
    """Check if docker-compose.dev.yml exists"""
    compose_file = "docker/docker-compose.dev.yml"
    if not os.path.exists(compose_file):
        print_colored(f"❌ Docker Compose file not found: {compose_file}", Colors.RED)
        return False
    return True

def get_docker_compose_hash() -> Optional[str]:
    """Create hash from docker-compose.dev.yml and requirements.txt"""
    compose_hash = get_file_hash("docker/docker-compose.dev.yml")
    requirements_hash = get_file_hash("backend/requirements.txt")
    dockerfile_hash = get_file_hash("backend/Dockerfile.simple")
    
    if not compose_hash:
        return None
    
    # Combine all relevant hashes
    combined = f"{compose_hash}:{requirements_hash or 'no-req'}:{dockerfile_hash or 'no-dockerfile'}"
    return hashlib.sha256(combined.encode()).hexdigest()

def get_stored_docker_hash() -> Optional[str]:
    """Read stored Docker hash"""
    hash_file = ".docker_state"
    try:
        with open(hash_file, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def store_docker_hash(hash_value: str) -> None:
    """Store current Docker hash"""
    hash_file = ".docker_state"
    with open(hash_file, "w") as f:
        f.write(hash_value)

def check_container_status() -> Dict[str, str]:
    """Check Docker container status - Windows compatible"""
    try:
        result = run_command("docker ps --format json", capture_output=True)
        if not result or result.returncode != 0:
            return {}
        
        containers = {}
        for line in result.stdout.strip().split('\n'):
            if line.strip():
                try:
                    container = json.loads(line)
                    name = container.get('Names', '').replace('ragflow-', '')
                    status = container.get('Status', '')
                    containers[name] = status
                except json.JSONDecodeError:
                    continue
        
        return containers
    except Exception as e:
        print_colored(f"❌ Container status check failed: {e}", Colors.RED)
        return {}

def test_http_endpoint(url: str, timeout: int = 5) -> tuple[bool, str, float]:
    """Test HTTP endpoint - Windows compatible"""
    start_time = time.time()
    try:
        response = requests.get(url, timeout=timeout)
        response_time = time.time() - start_time
        
        if response.status_code in [200, 404]:  # 404 can be OK for some endpoints
            return True, f"HTTP {response.status_code}", response_time
        else:
            return False, f"HTTP {response.status_code}", response_time
            
    except requests.exceptions.RequestException as e:
        response_time = time.time() - start_time
        return False, str(e), response_time

def test_tcp_port(host: str, port: int, timeout: int = 3) -> tuple[bool, str]:
    """Test TCP port - Windows compatible"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            return True, "Port reachable"
        else:
            return False, f"Connection failed (Code: {result})"
            
    except Exception as e:
        return False, str(e)

def wait_for_services() -> bool:
    """Windows-compatible service check"""
    services = {
        'Backend API': ('http', 'http://localhost:8000/ping'),
        'PostgreSQL': ('tcp', 'localhost:5432'),
        'Qdrant': ('http', 'http://localhost:6333/dashboard'),
        'Redis': ('tcp', 'localhost:6379')
    }
    
    max_wait = 120  # 2 minutes timeout
    print_colored("⏳ Waiting for services...", Colors.BLUE)
    
    all_healthy = True
    
    for service_name, (check_type, endpoint) in services.items():
        print(f"    Waiting for {service_name}...", end="", flush=True)
        
        start_time = time.time()
        ready = False
        
        while time.time() - start_time < max_wait and not ready:
            if check_type == 'http':
                success, message, resp_time = test_http_endpoint(endpoint)
                if success:
                    ready = True
                    print_colored(f" ✅ ({message}, {resp_time:.2f}s)", Colors.GREEN)
            
            elif check_type == 'tcp':
                host, port = endpoint.split(':')
                success, message = test_tcp_port(host, int(port))
                if success:
                    ready = True
                    print_colored(f" ✅ ({message})", Colors.GREEN)
            
            if not ready:
                time.sleep(2)
                print(".", end="", flush=True)
        
        if not ready:
            print_colored(f" ⏰ (Timeout - {service_name} might still be running)", Colors.YELLOW)
            all_healthy = False
    
    return all_healthy

def start_docker_services() -> bool:
    """Start Docker services"""
    if not check_docker_compose_file():
        return False
    
    print_colored("🐳 Starting Docker services...", Colors.BLUE)
    
    # Stop old containers
    print("  📦 Stopping old containers...")
    run_command("docker compose -f docker/docker-compose.dev.yml down", capture_output=False)
    
    # Start containers
    print("  🏗️  Building and starting containers...")
    result = run_command("docker compose -f docker/docker-compose.dev.yml up --build -d", capture_output=False)
    
    if result and result.returncode == 0:
        print_colored("✅ Docker services started!", Colors.GREEN)
        return True
    else:
        print_colored("❌ Error starting Docker services!", Colors.RED)
        return False

def show_project_info() -> None:
    """Show project information"""
    print_colored("🎯 RagFlow Backend Development Environment", Colors.CYAN)
    
    # Backend info
    try:
        with open("backend/requirements.txt", "r") as f:
            requirements = f.readlines()
        print(f"📦 Backend Dependencies: {len(requirements)} packages")
    except FileNotFoundError:
        print("📦 Backend: requirements.txt not found")
    
    # Docker info
    if check_docker_running():
        print_colored("🐳 Docker: ✅ Running", Colors.GREEN)
    else:
        print_colored("🐳 Docker: ❌ Not available", Colors.RED)

def show_service_urls() -> None:
    """Show service URLs and perform quick health check"""
    print_colored("\n🌐 Service URLs:", Colors.CYAN)
    print("   Backend API:      http://localhost:8000")
    print("   API Docs:         http://localhost:8000/docs")
    print("   Health Check:     http://localhost:8000/ping")
    print("   Qdrant Dashboard: http://localhost:6333/dashboard")
    print("   PostgreSQL:       localhost:5432 (ragflow/ragflow)")
    
    # Quick health test
    print_colored("\n🔍 Quick Health Check:", Colors.BLUE)
    
    # Test Backend
    success, message, resp_time = test_http_endpoint("http://localhost:8000/ping")
    if success:
        print_colored(f"   Backend: ✅ Running ({resp_time:.2f}s)", Colors.GREEN)
    else:
        print_colored(f"   Backend: ❌ {message}", Colors.RED)
    
    # Test Qdrant
    success, message, resp_time = test_http_endpoint("http://localhost:6333/dashboard")
    if success:
        print_colored(f"   Qdrant:  ✅ Running ({resp_time:.2f}s)", Colors.GREEN)
    else:
        print_colored(f"   Qdrant:  ❌ {message}", Colors.RED)

def show_success_message():
    """Show success message with next steps"""
    print_colored("\n🎉 Development Environment Ready!", Colors.GREEN + Colors.BOLD)
    print_colored("=" * 50, Colors.GREEN)
    print_colored("\n🚀 Next Steps:", Colors.CYAN)
    print("   1. Open API Documentation: http://localhost:8000/docs")
    print("   2. Test document upload via Swagger UI")
    print("   3. Check Qdrant dashboard: http://localhost:6333/dashboard")
    print("   4. Start building your RAG application!")
    
    print_colored("\n💡 Development Tips:", Colors.YELLOW)
    print("   • Use 'docker logs ragflow-backend' to view backend logs")
    print("   • API is available at http://localhost:8000")
    print("   • Hot reload is enabled for backend changes")
    print("   • Run 'python scripts/check_services.py' for health checks")

def cleanup_on_exit(signum, frame):
    """Cleanup on program exit"""
    print_colored("\n\n👋 Shutting down Development Environment...", Colors.YELLOW)
    print("   Containers will keep running. Use 'docker compose -f docker/docker-compose.dev.yml down' to stop.")
    sys.exit(0)

def main():
    """Main function"""
    # Signal handler for clean shutdown
    signal.signal(signal.SIGINT, cleanup_on_exit)
    signal.signal(signal.SIGTERM, cleanup_on_exit)
    
    print_colored("🚀 RagFlow Backend Development Setup", Colors.BOLD + Colors.GREEN)
    print("=" * 50)
    
    # Show project info
    show_project_info()
    
    # Check Docker
    if not check_docker_running():
        print_colored("❌ Docker is not available! Please start Docker Desktop.", Colors.RED)
        return 1
    
    # Hash-based change detection
    current_hash = get_docker_compose_hash()
    stored_hash = get_stored_docker_hash()
    
    if current_hash != stored_hash:
        print_colored("🔄 Docker configuration or dependencies have changed", Colors.YELLOW)
        needs_restart = True
    else:
        # Check if containers are running
        containers = check_container_status()
        required_containers = ["backend", "postgres", "redis", "qdrant"]
        running_containers = [name for name, status in containers.items() 
                            if name in required_containers and "Up" in status]
        
        if len(running_containers) == len(required_containers):
            print_colored("✅ All services are already running", Colors.GREEN)
            needs_restart = False
        else:
            print_colored("🔄 Services need to be started", Colors.YELLOW)
            needs_restart = True
    
    if needs_restart:
        # Start Docker services
        if not start_docker_services():
            return 1
        
        # Store new hash
        if current_hash:
            store_docker_hash(current_hash)
    
    # Wait for services to be ready
    services_ready = wait_for_services()
    
    # Show service URLs and status
    show_service_urls()
    
    if services_ready:
        show_success_message()
        print_colored("\n💡 Tip: Use 'python scripts/check_services.py' for detailed health checks", Colors.CYAN)
    else:
        print_colored("\n⚠️  Some services may not be fully ready yet", Colors.YELLOW)
        print_colored("   But don't worry - they might still be starting up!", Colors.YELLOW)
        print_colored("   Try opening http://localhost:8000/docs in a few moments", Colors.CYAN)
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        cleanup_on_exit(None, None)
    except Exception as e:
        print_colored(f"\n❌ Unexpected error: {e}", Colors.RED)
        sys.exit(1)