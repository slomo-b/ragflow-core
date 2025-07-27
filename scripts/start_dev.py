#!/usr/bin/env python3
"""
Fixed Smart Development Environment Script
- Corrected container detection logic
- Better parsing of docker ps output
- Improved debugging
"""

import subprocess
import sys
import time
import requests
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class RagFlowDev:
    def __init__(self):
        self.base_path = Path.cwd()
        self.docker_compose_file = "docker/docker-compose.dev.yml"
        self.backend_path = self.base_path / "backend"
        self.requirements_file = self.backend_path / "requirements.txt"
        
    def run_command(self, cmd: List[str], check: bool = True, capture_output: bool = True) -> subprocess.CompletedProcess:
        """Run command with logging"""
        print(f"🔧 Running: {' '.join(cmd)}")
        try:
            result = subprocess.run(cmd, check=check, capture_output=capture_output, text=True)
            if result.stdout and capture_output:
                # Only show first few lines to avoid spam
                output_lines = result.stdout.strip().split('\n')
                if len(output_lines) <= 3:
                    print(f"📤 Output: {result.stdout.strip()}")
                else:
                    print(f"📤 Output: {output_lines[0]}... ({len(output_lines)} lines)")
            return result
        except subprocess.CalledProcessError as e:
            print(f"❌ Command failed: {e}")
            if e.stderr and capture_output:
                print(f"📥 Error: {e.stderr.strip()}")
            if check:
                raise
            return e

    def check_docker(self) -> bool:
        """Check if Docker is available"""
        try:
            result = self.run_command(["docker", "--version"])
            print("✅ Docker is available")
            return True
        except subprocess.CalledProcessError:
            print("❌ Docker is not running or not installed")
            return False

    def get_container_status(self) -> Dict[str, str]:
        """Get status of all RagFlow containers - FIXED VERSION"""
        try:
            result = self.run_command([
                "docker", "ps", "-a", 
                "--filter", "name=ragflow",
                "--format", "{{.Names}}\t{{.Status}}"
            ], check=False)
            
            containers = {}
            if result.returncode == 0 and result.stdout.strip():
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line.strip() and '\t' in line:
                        parts = line.split('\t', 1)
                        if len(parts) == 2:
                            name = parts[0].strip()
                            status = parts[1].strip()
                            containers[name] = status
                            print(f"   Found: {name} → {status}")
            
            return containers
        except Exception as e:
            print(f"❌ Error getting container status: {e}")
            return {}

    def check_backend_health(self, timeout: int = 30) -> bool:
        """Check if backend is healthy"""
        print("🔍 Checking backend health...")
        
        for i in range(timeout):
            try:
                response = requests.get("http://localhost:8000/ping", timeout=5)
                if response.status_code == 200:
                    print("✅ Backend is healthy!")
                    return True
            except requests.exceptions.RequestException:
                pass
            
            if i % 10 == 0 and i > 0:
                print(f"⏳ Still waiting for backend... ({i}s)")
            time.sleep(1)
        
        print("❌ Backend health check failed")
        return False

    def get_backend_logs(self, lines: int = 30) -> str:
        """Get recent backend logs"""
        try:
            result = self.run_command([
                "docker", "logs", "--tail", str(lines), "ragflow-backend"
            ], check=False)
            
            if result.returncode == 0:
                return result.stdout
            return f"Failed to get logs: {result.stderr}"
        except:
            return "Failed to get logs - container may not exist"

    def diagnose_backend_problem(self) -> str:
        """Diagnose specific backend problems"""
        print("🔍 Diagnosing backend problem...")
        
        # Check if container exists
        containers = self.get_container_status()
        if "ragflow-backend" not in containers:
            return "container_missing"
        
        status = containers["ragflow-backend"]
        
        if "healthy" in status.lower():
            return "healthy"
        elif "unhealthy" in status.lower():
            # Get logs to determine why unhealthy
            logs = self.get_backend_logs(50)
            
            if "sqlalchemy" in logs.lower() and "table" in logs.lower() and "already defined" in logs.lower():
                return "sqlalchemy_conflict"
            elif "modulenotfounderror" in logs.lower():
                return "missing_dependencies"
            elif "importerror" in logs.lower():
                return "import_error"
            elif "connection" in logs.lower() and ("refused" in logs.lower() or "failed" in logs.lower()):
                return "connection_error"
            else:
                return "unknown_unhealthy"
        elif "exited" in status.lower():
            return "container_exited"
        else:
            return "unknown_status"

    def fix_sqlalchemy_conflict(self):
        """Fix the SQLAlchemy table conflict"""
        print("🔧 Fixing SQLAlchemy table conflict...")
        
        collection_file = self.backend_path / "app" / "models" / "collection.py"
        
        fixed_content = '''from sqlalchemy import Column, String, Text, DateTime, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from ..core.database import Base

class Collection(Base):
    __tablename__ = "collections"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    documents_count = Column(Integer, default=0)
    total_chunks = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_data = Column(JSON, default=dict)
    
    documents = relationship("Document", back_populates="collection")
    
    def __repr__(self):
        return f"<Collection(id={self.id}, name='{self.name}', documents={self.documents_count})>"
'''
        
        # Backup and fix
        if collection_file.exists():
            backup_file = collection_file.with_suffix('.py.backup')
            backup_file.write_text(collection_file.read_text())
            print(f"✅ Backed up to {backup_file}")
        
        collection_file.write_text(fixed_content)
        print("✅ Fixed SQLAlchemy model conflict")

    def restart_backend(self):
        """Restart just the backend container"""
        print("🔄 Restarting backend container...")
        self.run_command([
            "docker", "compose", "-f", self.docker_compose_file,
            "restart", "backend"
        ], check=False)

    def start_services_smart(self) -> bool:
        """Smart service startup based on current state"""
        print("🚀 Smart service startup...")
        
        containers = self.get_container_status()
        
        # Check what's running
        databases_running = all(
            name in containers and "healthy" in containers[name].lower()
            for name in ["ragflow-postgres", "ragflow-qdrant", "ragflow-redis"]
        )
        
        if not databases_running:
            print("📊 Starting database services...")
            self.run_command([
                "docker", "compose", "-f", self.docker_compose_file,
                "up", "-d", "postgres", "qdrant", "redis"
            ], check=False)
            
            print("⏳ Waiting for databases...")
            time.sleep(15)
        else:
            print("✅ Database services already running")
        
        # Handle backend based on diagnosis
        backend_problem = self.diagnose_backend_problem()
        print(f"🎯 Backend diagnosis: {backend_problem}")
        
        if backend_problem == "sqlalchemy_conflict":
            self.fix_sqlalchemy_conflict()
            self.restart_backend()
        elif backend_problem == "container_missing":
            print("🔨 Starting backend...")
            self.run_command([
                "docker", "compose", "-f", self.docker_compose_file,
                "up", "-d", "backend"
            ], check=False)
        elif backend_problem == "container_exited":
            print("🔄 Restarting exited backend...")
            self.restart_backend()
        elif backend_problem == "unknown_unhealthy":
            print("⚠️ Backend unhealthy, restarting...")
            self.restart_backend()
        
        # Start frontend if needed
        if "ragflow-frontend" not in containers:
            print("🎨 Starting frontend...")
            self.run_command([
                "docker", "compose", "-f", self.docker_compose_file,
                "up", "-d", "frontend"
            ], check=False)
        
        return True

    def show_final_status(self):
        """Show final status and URLs"""
        print("\n" + "="*50)
        print("🎉 RagFlow Development Environment")
        print("="*50)
        
        # Check services
        backend_healthy = False
        try:
            response = requests.get("http://localhost:8000/ping", timeout=5)
            backend_healthy = response.status_code == 200
        except:
            pass
        
        if backend_healthy:
            print("✅ Backend is running and healthy!")
            print("\n📊 Available Services:")
            print("   🔗 Backend API:      http://localhost:8000")
            print("   📚 API Documentation: http://localhost:8000/docs")
            print("   🎨 Frontend:         http://localhost:3000")
            print("   🔍 Qdrant Dashboard: http://localhost:6333/dashboard")
            
            print("\n🧪 Quick Tests:")
            print("   curl http://localhost:8000/ping")
            print("   curl http://localhost:8000/api/v1/health/")
            
        else:
            print("⚠️ Backend not fully healthy yet")
            print("\n🔍 Debug Commands:")
            print("   docker logs ragflow-backend -f")
            print("   docker exec -it ragflow-backend bash")
            print("   curl http://localhost:8000/ping")
        
        print("\n🛠️ Management:")
        print("   📜 Logs:    docker compose -f docker/docker-compose.dev.yml logs -f")
        print("   🔄 Restart: docker compose -f docker/docker-compose.dev.yml restart")
        print("   🛑 Stop:    docker compose -f docker/docker-compose.dev.yml down")

    def main(self):
        """Main execution flow"""
        print("🚀 RagFlow Smart Development Environment (Fixed)")
        print("="*55)
        
        # Check Docker
        if not self.check_docker():
            sys.exit(1)
        
        # Get current status
        print("\n📊 Current container status:")
        containers = self.get_container_status()
        
        if not containers:
            print("   No RagFlow containers found")
            print("\n🔨 Starting fresh environment...")
            self.run_command([
                "docker", "compose", "-f", self.docker_compose_file,
                "up", "-d"
            ], check=False)
        else:
            print(f"   Found {len(containers)} containers")
            
            # Smart startup based on current state
            self.start_services_smart()
        
        # Wait and check final status
        print("\n⏳ Waiting for services to stabilize...")
        time.sleep(20)
        
        # Final health check
        backend_healthy = self.check_backend_health(timeout=30)
        
        self.show_final_status()
        
        return backend_healthy

if __name__ == "__main__":
    dev = RagFlowDev()
    success = dev.main()
    sys.exit(0 if success else 1)