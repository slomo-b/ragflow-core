#!/usr/bin/env python3
"""
Windows-Compatible RagFlow Service Checker
Ersetzt die fehlerhafte start_dev.py Health-Check Logik
"""

import requests
import socket
import time
import subprocess
import sys

def test_http(url, expected_codes=[200, 404]):
    """Test HTTP endpoint"""
    try:
        response = requests.get(url, timeout=5)
        return response.status_code in expected_codes, response.status_code
    except Exception as e:
        return False, str(e)

def test_tcp_port(host, port):
    """Test TCP port connection"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0, result
    except Exception as e:
        return False, str(e)

def check_docker_containers():
    """Check Docker container status"""
    try:
        result = subprocess.run(['docker', 'ps', '--format', 'table {{.Names}}\t{{.Status}}'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("🐳 Docker Container Status:")
            print(result.stdout)
            return True
        else:
            print("❌ Docker nicht verfügbar")
            return False
    except Exception as e:
        print(f"❌ Docker check failed: {e}")
        return False

def main():
    print("🚀 RagFlow Service Health Check (Windows Compatible)")
    print("=" * 60)
    
    # Check Docker containers first
    docker_ok = check_docker_containers()
    print()
    
    if not docker_ok:
        print("❌ Docker containers not available")
        return 1
    
    # Test services
    services = [
        ("Backend API", "http", "http://localhost:8000/ping"),
        ("Backend Root", "http", "http://localhost:8000/"),
        ("API Docs", "http", "http://localhost:8000/docs"),
        ("Qdrant Dashboard", "http", "http://localhost:6333/dashboard"),
        ("Qdrant API", "http", "http://localhost:6333/collections"),
        ("PostgreSQL", "tcp", "localhost:5432"),
        ("Redis", "tcp", "localhost:6379"),
    ]
    
    print("🔍 Service Connectivity Tests:")
    print("-" * 60)
    
    all_good = True
    
    for name, test_type, endpoint in services:
        print(f"  {name:<20} ... ", end="", flush=True)
        
        if test_type == "http":
            success, result = test_http(endpoint)
            if success:
                print(f"✅ (HTTP {result})")
            else:
                print(f"❌ ({result})")
                all_good = False
                
        elif test_type == "tcp":
            host, port = endpoint.split(":")
            success, result = test_tcp_port(host, int(port))
            if success:
                print(f"✅ (Connected)")
            else:
                print(f"❌ (Connection failed: {result})")
                all_good = False
    
    print("-" * 60)
    
    if all_good:
        print("🎉 All services are healthy!")
        print()
        print("🌐 Access your services:")
        print("   Backend API:      http://localhost:8000")
        print("   API Docs:         http://localhost:8000/docs")
        print("   Qdrant Dashboard: http://localhost:6333/dashboard")
        print()
        print("✅ Your RagFlow development environment is ready!")
        return 0
    else:
        print("⚠️  Some services have issues")
        print("💡 Try: docker compose -f docker/docker-compose.dev.yml restart")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n👋 Health check interrupted")
        sys.exit(1)