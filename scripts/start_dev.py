#!/usr/bin/env python3
import subprocess
import sys
import os
import json
import hashlib
from pathlib import Path

def run_command(command, cwd=None, check=True):
    """Führt einen Befehl aus und gibt das Ergebnis zurück"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd, 
            check=check,
            capture_output=True,
            text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        print(f"Fehler beim Ausführen von '{command}': {e}")
        return None

def get_file_hash(filepath):
    """Erstellt MD5 Hash einer Datei"""
    try:
        with open(filepath, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except FileNotFoundError:
        return None

def get_dependency_state_hash():
    """Erstellt einen kombinierten Hash aus package.json und package-lock.json"""
    package_hash = get_file_hash("package.json")
    lock_hash = get_file_hash("package-lock.json")
    
    if not package_hash:
        return None
    
    # Kombiniere beide Hashes
    combined = f"{package_hash}:{lock_hash or 'no-lock'}"
    return hashlib.md5(combined.encode()).hexdigest()

def get_stored_dependency_hash():
    """Liest den gespeicherten Dependency-Hash"""
    hash_file = ".dependency_state"
    try:
        with open(hash_file, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def store_dependency_hash(hash_value):
    """Speichert den aktuellen Dependency-Hash"""
    hash_file = ".dependency_state"
    with open(hash_file, "w") as f:
        f.write(hash_value)

def check_node_modules_integrity():
    """Prüft ob node_modules vollständig ist"""
    if not os.path.exists("node_modules"):
        return False
    
    # Prüfe ob wichtige Dependencies vorhanden sind
    try:
        with open("package.json", "r") as f:
            package_data = json.load(f)
        
        dependencies = package_data.get("dependencies", {})
        dev_dependencies = package_data.get("devDependencies", {})
        
        # Prüfe einige wichtige Dependencies
        important_deps = list(dependencies.keys())[:3]  # Erste 3 Dependencies
        
        for dep in important_deps:
            dep_path = os.path.join("node_modules", dep)
            if not os.path.exists(dep_path):
                print(f"Wichtige Dependency fehlt: {dep}")
                return False
        
        return True
    except Exception as e:
        print(f"Fehler bei node_modules Integritätsprüfung: {e}")
        return False

def should_install_dependencies():
    """Entscheidet ob Dependencies installiert werden müssen"""
    # 1. Prüfe ob node_modules existiert und vollständig ist
    if not check_node_modules_integrity():
        print("node_modules unvollständig oder nicht vorhanden")
        return True
    
    # 2. Prüfe ob package.json oder package-lock.json geändert wurde
    current_hash = get_dependency_state_hash()
    stored_hash = get_stored_dependency_hash()
    
    if not current_hash:
        print("Fehler beim Lesen der package.json")
        return True
    
    if current_hash != stored_hash:
        print("Package-Dateien wurden geändert")
        return True
    
    print("✅ Dependencies sind aktuell - Installation übersprungen")
    return False

def install_dependencies_smart():
    """Intelligente Dependency-Installation"""
    if not should_install_dependencies():
        return True
    
    print("📦 Installiere Dependencies...")
    
    # Bestimme besten Installationsbefehl
    if os.path.exists("package-lock.json"):
        # npm ci ist schneller und deterministischer
        command = "npm ci"
        print("Verwende 'npm ci' (package-lock.json gefunden)")
    else:
        command = "npm install"
        print("Verwende 'npm install'")
    
    result = run_command(command)
    
    if result and result.returncode == 0:
        # Speichere neuen Hash
        current_hash = get_dependency_state_hash()
        if current_hash:
            store_dependency_hash(current_hash)
        print("✅ Dependencies erfolgreich installiert!")
        return True
    else:
        print("❌ Fehler bei der Installation!")
        return False

def show_project_info():
    """Zeigt Projekt-Informationen"""
    try:
        with open("package.json", "r") as f:
            package_data = json.load(f)
        
        name = package_data.get("name", "Unbekannt")
        version = package_data.get("version", "0.0.0")
        
        print(f"🎯 Projekt: {name} (v{version})")
        
        # Zeige wichtige Scripts
        scripts = package_data.get("scripts", {})
        if "dev" in scripts:
            print(f"🔧 Dev Command: {scripts['dev']}")
            
    except Exception:
        pass

def main():
    print("🚀 SwapSwiss.ch Development Setup")
    print("=" * 40)
    
    # Zeige Projekt-Info
    show_project_info()
    
    # Prüfe ob package.json existiert
    if not os.path.exists("package.json"):
        print("❌ package.json nicht gefunden!")
        sys.exit(1)
    
    # Installiere Dependencies intelligent
    if not install_dependencies_smart():
        sys.exit(1)
    
    print("\n🌐 Starte Development Server...")
    print("Öffnen Sie http://localhost:5173 in Ihrem Browser")
    print("Drücken Sie Ctrl+C zum Beenden\n")
    
    # Starte Development Server
    try:
        subprocess.run("npm run dev", shell=True, check=True)
    except KeyboardInterrupt:
        print("\n👋 Development Server beendet")
    except subprocess.CalledProcessError as e:
        print(f"❌ Fehler beim Starten: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()