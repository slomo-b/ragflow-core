#!/usr/bin/env python3
"""
RagFlow Backend Development Starter
Intelligente Dependencies-Prüfung und sauberer Backend-Start
"""

import subprocess
import sys
import os
import json
import hashlib
import time
import signal
from pathlib import Path
from typing import Optional, Dict, Any

def run_command(command: str, cwd: Optional[str] = None, check: bool = True, capture_output: bool = True) -> Optional[subprocess.CompletedProcess]:
    """Führt einen Befehl aus und gibt das Ergebnis zurück"""
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
            print(f"❌ Fehler beim Ausführen von '{command}': {e}")
            if e.stdout:
                print(f"STDOUT: {e.stdout}")
            if e.stderr:
                print(f"STDERR: {e.stderr}")
        return None

def get_file_hash(filepath: str) -> Optional[str]:
    """Erstellt SHA256 Hash einer Datei"""
    try:
        with open(filepath, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except FileNotFoundError:
        return None

def check_docker_running() -> bool:
    """Prüft ob Docker läuft"""
    result = run_command("docker info", capture_output=True)
    return result is not None and result.returncode == 0

def check_docker_compose_file() -> bool:
    """Prüft ob docker-compose.dev.yml existiert"""
    compose_file = "docker/docker-compose.dev.yml"
    if not os.path.exists(compose_file):
        print(f"❌ Docker Compose file nicht gefunden: {compose_file}")
        return False
    return True

def get_docker_compose_hash() -> Optional[str]:
    """Erstellt Hash aus docker-compose.dev.yml und requirements.txt"""
    compose_hash = get_file_hash("docker/docker-compose.dev.yml")
    requirements_hash = get_file_hash("backend/requirements.txt")
    dockerfile_hash = get_file_hash("backend/Dockerfile.dev")
    
    if not compose_hash:
        return None
    
    # Kombiniere alle relevanten Hashes
    combined = f"{compose_hash}:{requirements_hash or 'no-req'}:{dockerfile_hash or 'no-dockerfile'}"
    return hashlib.sha256(combined.encode()).hexdigest()

def get_stored_docker_hash() -> Optional[str]:
    """Liest den gespeicherten Docker-Hash"""
    hash_file = ".docker_state"
    try:
        with open(hash_file, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def store_docker_hash(hash_value: str) -> None:
    """Speichert den aktuellen Docker-Hash"""
    hash_file = ".docker_state"
    with open(hash_file, "w") as f:
        f.write(hash_value)

def check_containers_running() -> Dict[str, bool]:
    """Prüft welche Container laufen"""
    result = run_command("docker compose -f docker/docker-compose.dev.yml ps --format json", capture_output=True)
    
    if not result or result.returncode != 0:
        return {}
    
    containers_status = {}
    try:
        # Parse JSON output
        for line in result.stdout.strip().split('\n'):
            if line.strip():
                container = json.loads(line)
                service = container.get('Service', '')
                state = container.get('State', '')
                containers_status[service] = state == 'running'
    except (json.JSONDecodeError, KeyError):
        # Fallback: einfache Textausgabe parsen
        result = run_command("docker compose -f docker/docker-compose.dev.yml ps", capture_output=True)
        if result and result.returncode == 0:
            lines = result.stdout.split('\n')
            for line in lines[1:]:  # Skip header
                if line.strip() and 'Up' in line:
                    parts = line.split()
                    if len(parts) > 0:
                        service_name = parts[0].split('_')[-1].split('-')[0]  # Extract service name
                        containers_status[service_name] = True
    
    return containers_status

def should_rebuild_containers() -> bool:
    """Entscheidet ob Container neu gebaut werden müssen"""
    # 1. Prüfe ob Docker Compose Hash sich geändert hat
    current_hash = get_docker_compose_hash()
    stored_hash = get_stored_docker_hash()
    
    if not current_hash:
        print("❌ Fehler beim Lesen der Docker-Konfiguration")
        return True
    
    if current_hash != stored_hash:
        print("🔄 Docker-Konfiguration oder Dependencies haben sich geändert")
        return True
    
    # 2. Prüfe ob alle wichtigen Container laufen
    containers = check_containers_running()
    required_services = ['backend', 'postgres', 'qdrant', 'redis']
    
    missing_services = []
    for service in required_services:
        if not containers.get(service, False):
            missing_services.append(service)
    
    if missing_services:
        print(f"🔄 Folgende Services laufen nicht: {', '.join(missing_services)}")
        return True
    
    print("✅ Alle Container laufen bereits - Rebuild übersprungen")
    return False

def start_docker_services() -> bool:
    """Startet Docker Services intelligent"""
    if not should_rebuild_containers():
        return True
    
    print("🐳 Starte Docker Services...")
    
    # Stoppe eventuell laufende Container
    print("  📦 Stoppe alte Container...")
    run_command("docker compose -f docker/docker-compose.dev.yml down", capture_output=False)
    
    # Baue und starte Container
    print("  🏗️  Baue und starte Container...")
    result = run_command("docker compose -f docker/docker-compose.dev.yml up --build -d", capture_output=False)
    
    if result and result.returncode == 0:
        # Speichere neuen Hash
        current_hash = get_docker_compose_hash()
        if current_hash:
            store_docker_hash(current_hash)
        
        # Warte auf Services
        print("  ⏳ Warte auf Services...")
        wait_for_services()
        
        print("✅ Docker Services erfolgreich gestartet!")
        return True
    else:
        print("❌ Fehler beim Starten der Docker Services!")
        return False

def wait_for_services() -> None:
    """Wartet bis alle Services bereit sind"""
    services = {
        'Backend API': 'http://localhost:8000/ping',
        'PostgreSQL': 'localhost:5432',
        'Qdrant': 'http://localhost:6333/dashboard',
        'Redis': 'localhost:6379'
    }
    
    max_wait = 60  # Sekunden
    for service_name, endpoint in services.items():
        print(f"    Warte auf {service_name}...", end="", flush=True)
        
        start_time = time.time()
        ready = False
        
        while time.time() - start_time < max_wait and not ready:
            if 'http' in endpoint:
                # HTTP Check
                result = run_command(f"curl -s -o /dev/null -w '%{{http_code}}' {endpoint}", capture_output=True)
                if result and result.stdout.strip() in ['200', '404']:  # 404 is OK for some endpoints
                    ready = True
            else:
                # Port Check
                host, port = endpoint.split(':')
                result = run_command(f"nc -z {host} {port}", capture_output=True)
                if result and result.returncode == 0:
                    ready = True
            
            if not ready:
                time.sleep(2)
                print(".", end="", flush=True)
        
        if ready:
            print(" ✅")
        else:
            print(" ⏰ (Timeout, aber Service könnte trotzdem laufen)")

def show_project_info() -> None:
    """Zeigt Projekt-Informationen"""
    print("🎯 RagFlow Backend Development Environment")
    
    # Backend Info
    try:
        with open("backend/requirements.txt", "r") as f:
            requirements = f.readlines()
        print(f"📦 Backend Dependencies: {len(requirements)} packages")
    except FileNotFoundError:
        print("📦 Backend: requirements.txt nicht gefunden")
    
    # Docker Info
    if check_docker_running():
        print("🐳 Docker: ✅ Läuft")
    else:
        print("🐳 Docker: ❌ Nicht verfügbar")

def show_service_urls() -> None:
    """Zeigt Service URLs"""
    print("\n🌐 Service URLs:")
    print("   Backend API:     http://localhost:8000")
    print("   API Docs:        http://localhost:8000/docs")
    print("   Health Check:    http://localhost:8000/ping")
    print("   Qdrant Dashboard: http://localhost:6333/dashboard")
    print("   PostgreSQL:      localhost:5432 (ragflow/ragflow)")
    print("\n💡 Tipp: Benutze 'docker compose -f docker/docker-compose.dev.yml logs -f' für Live-Logs")

def cleanup_on_exit(signum, frame):
    """Cleanup bei Programmende"""
    print("\n\n👋 Beende Development Environment...")
    print("   Container bleiben laufen. Zum Stoppen:")
    print("   docker compose -f docker/docker-compose.dev.yml down")
    sys.exit(0)

def main():
    # Signal Handler für sauberes Beenden
    signal.signal(signal.SIGINT, cleanup_on_exit)
    signal.signal(signal.SIGTERM, cleanup_on_exit)
    
    print("🚀 RagFlow Backend Development Setup")
    print("=" * 50)
    
    # Zeige Projekt-Info
    show_project_info()
    
    # Prüfe Voraussetzungen
    if not check_docker_running():
        print("❌ Docker ist nicht verfügbar! Bitte starten Sie Docker Desktop.")
        sys.exit(1)
    
    if not check_docker_compose_file():
        sys.exit(1)
    
    # Starte Docker Services
    if not start_docker_services():
        sys.exit(1)
    
    # Zeige Service URLs
    show_service_urls()
    
    print("\n🎉 Development Environment ist bereit!")
    print("📋 Drücken Sie Ctrl+C zum Beenden (Container bleiben laufen)")
    
    # Halte Script am Leben
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        cleanup_on_exit(None, None)

if __name__ == "__main__":
    main()